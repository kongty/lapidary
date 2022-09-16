import simpy
from abc import ABC, abstractmethod
from typing import Generator, Any, List
from lapidary.accelerator import Accelerator, PartitionType
from lapidary.components import PRR, Bank
from lapidary.task_queue import TaskQueue
from lapidary.task import Task
from lapidary.app import AppConfig, AppPool, NoAppConfigError
import logging
import math
logger = logging.getLogger(__name__)


class Scheduler(ABC):
    def __init__(self, env: simpy.Environment) -> None:
        self.env = env
        self.app_pool: AppPool

    def set_app_pool(self, app_pool: AppPool) -> None:
        self.app_pool = app_pool

    def run(self, accelerator: Accelerator) -> None:
        self.env.process(self.proc_schedule(accelerator))

    @abstractmethod
    def proc_schedule(self, accelerator: Accelerator) -> Generator[simpy.events.Event, Any, Any]:
        pass

    @abstractmethod
    def schedule(self, accelerator: Accelerator) -> Generator[simpy.events.Event, None, None]:
        pass

class RoundRobinScheduler(Scheduler):
    def __init__(self, env: simpy.Environment) -> None:
        super().__init__(env)
        self.task_queue = TaskQueue(self.env, maxsize=40000)
        self.schedule_delay = 1157

    def proc_schedule(self, accelerator: Accelerator) -> Generator[simpy.events.Event, simpy.events.ConditionValue,
                                                                   None]:
        """Call schedule function when new tasks arrive or old tasks finish."""
        while True:
            triggered = yield self.task_queue.evt_task_arrive | accelerator.evt_task_done
            if accelerator.evt_task_done in triggered:
                task, interrupt = triggered[accelerator.evt_task_done]
                self.task_queue.update_dependency(done=task)
                accelerator.acknowledge_task_done(interrupt)
            yield self.env.process(self.schedule(accelerator))

    def schedule(self, accelerator: Accelerator) -> Generator[simpy.events.Event, None, None]:
        """Schedule tasks on the accelerator and return a list of tasks that are scheduled."""
        logger.info(f"[@ {self.env.now}] Call schedule.")
        tasks = self.select_tasks_prrs(accelerator=accelerator)
        logger.info(f"[@ {self.env.now}] Number of tasks being scheduled: {len(tasks)}")
        # schedule delay
        yield self.env.timeout(self.schedule_delay)

        for task in tasks:
            logger.info(f"[@ {self.env.now}] {task.tag} is scheduled to prr {list(map(lambda x: x.id, task.prrs))}, "
                        f"bank {list(map(lambda x: x.id, task.banks))}.")
            yield self.env.process(self.task_queue.remove(task))
            task.ts_schedule = int(self.env.now)
            accelerator.execute(task)

    def select_tasks_prrs(self, accelerator: Accelerator) -> List[Task]:
        # list of tasks that are scheduled
        tasks = []

        # Search all tasks in the task queue
        q_tmp = self.task_queue.q.copy()
        for task in q_tmp:
            # Break if the task cannot be mapped.
            if len(task.deps) != 0:
                break

            # Get app_config candidates from an app_pool
            app_config_list = self.app_pool.get(task.app)
            # Raise an error if there is no possible app config
            if len(app_config_list) == 0:
                raise NoAppConfigError(f"There is no app_config for {task.app} in the app_pool.")

            # TODO: Optimize by choosing the best bitstream from the app_pool.
            # For now, we just use the first available app_config from the app_pool.
            is_mapped = False
            runtime = 0
            selected_app_config: AppConfig = None
            selected_prrs: List[PRR] = []
            selected_banks: List[Bank] = []
            for app_config in app_config_list:
                # if accelerator.config.partition == PartitionType.FIXED:
                #     if max(int(math.ceil((app_config.input + app_config.output) / (accelerator.config.num_glb_banks // accelerator.config.num_prr_width))), app_config.prr_shape[1]) > 2:
                #         continue
                prrs, banks = accelerator.map(app_config)
                if len(prrs) > 0:
                    if runtime == 0:
                        runtime = app_config.runtime
                        selected_app_config = app_config
                        selected_prrs = prrs
                        selected_banks = banks
                    elif app_config.runtime < runtime:
                        runtime = app_config.runtime
                        selected_app_config = app_config
                        selected_prrs = prrs
                        selected_banks = banks
                    is_mapped = True

            # Break if any app_config is not mappable
            if is_mapped is False:
                break

            # Set app_config for the task
            task.set_app_config(selected_app_config)
            accelerator.allocate(task, selected_prrs, selected_banks)
            tasks.append(task)

        return tasks


class GreedyScheduler(Scheduler):
    def __init__(self, env: simpy.Environment) -> None:
        super().__init__(env)
        self.task_queue = TaskQueue(self.env, maxsize=40000)
        self.schedule_delay = 1157

    def proc_schedule(self, accelerator: Accelerator) -> Generator[simpy.events.Event, simpy.events.ConditionValue,
                                                                   None]:
        """Call schedule function when new tasks arrive or old tasks finish."""
        while True:
            triggered = yield self.task_queue.evt_task_arrive | accelerator.evt_task_done
            if accelerator.evt_task_done in triggered:
                task, interrupt = triggered[accelerator.evt_task_done]
                self.task_queue.update_dependency(done=task)
                accelerator.acknowledge_task_done(interrupt)
            yield self.env.process(self.schedule(accelerator))

    def schedule(self, accelerator: Accelerator) -> Generator[simpy.events.Event, None, None]:
        """Schedule tasks on the accelerator and return a list of tasks that are scheduled."""
        logger.info(f"[@ {self.env.now}] Call schedule.")
        tasks = self.select_tasks_prrs(accelerator=accelerator)
        logger.info(f"[@ {self.env.now}] Number of tasks being scheduled: {len(tasks)}")
        # schedule delay
        yield self.env.timeout(self.schedule_delay)

        for task in tasks:
            logger.info(f"[@ {self.env.now}] {task.tag} is scheduled to prr {list(map(lambda x: x.id, task.prrs))}, "
                        f"bank {list(map(lambda x: x.id, task.banks))}.")
            yield self.env.process(self.task_queue.remove(task))
            task.ts_schedule = int(self.env.now)
            accelerator.execute(task)

    def select_tasks_prrs(self, accelerator: Accelerator) -> List[Task]:
        # list of tasks that are scheduled
        tasks = []

        # Search all tasks in the task queue
        q_tmp = self.task_queue.q.copy()
        for task in q_tmp:
            # Break if the task cannot be mapped.
            if len(task.deps) != 0:
                break

            # Get app_config candidates from an app_pool
            app_config_list = self.app_pool.get(task.app)
            # Raise an error if there is no possible app config
            if len(app_config_list) == 0:
                raise NoAppConfigError(f"There is no app_config for {task.app} in the app_pool.")

            # TODO: Optimize by choosing the best bitstream from the app_pool.
            # For now, we just use the first available app_config from the app_pool.
            is_mapped = False
            runtime = 0
            selected_app_config: AppConfig = None
            selected_prrs: List[PRR] = []
            selected_banks: List[Bank] = []
            for app_config in app_config_list:
                # if accelerator.config.partition == PartitionType.FIXED:
                #     if max(int(math.ceil((app_config.input + app_config.output) / (accelerator.config.num_glb_banks // accelerator.config.num_prr_width))), app_config.prr_shape[1]) > 2:
                #         continue
                prrs, banks = accelerator.map(app_config)
                if len(prrs) > 0:
                    if runtime == 0:
                        runtime = app_config.runtime
                        selected_app_config = app_config
                        selected_prrs = prrs
                        selected_banks = banks
                    elif app_config.runtime < runtime:
                        runtime = app_config.runtime
                        selected_app_config = app_config
                        selected_prrs = prrs
                        selected_banks = banks
                    is_mapped = True

            # Break if any app_config is not mappable
            if is_mapped is False:
                break

            # Set app_config for the task
            task.set_app_config(selected_app_config)
            accelerator.allocate(task, selected_prrs, selected_banks)
            tasks.append(task)

        return tasks
