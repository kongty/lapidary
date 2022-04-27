import simpy
from abc import ABC, abstractmethod
from typing import List, Generator, Any
from lapidary.accelerator import Accelerator
from lapidary.task_queue import TaskQueue
from lapidary.app import AppPool
from lapidary.task import Task
import logging
logger = logging.getLogger(__name__)

class Scheduler(ABC):
    def __init__(self, env: simpy.Environment) -> None:
        self.env = env
        self.task_queue = TaskQueue(self.env)
        self.task_log: List[Task] = []
        self.app_pool: AppPool

    def set_app_pool(self, app_pool: AppPool) -> None:
        self.app_pool = app_pool

    def run(self, accelerator: Accelerator) -> None:
        self.env.process(self.proc_schedule(accelerator))

    @abstractmethod
    def proc_schedule(self, accelerator: Accelerator) -> Generator[simpy.events.Event, Any, Any]:
        pass

    @abstractmethod
    def schedule(self, accelerator: Accelerator) -> None:
        pass


class GreedyScheduler(Scheduler):
    def __init__(self, env: simpy.Environment) -> None:
        super().__init__(env)

    def proc_schedule(self, accelerator: Accelerator) -> Generator[simpy.events.Event, simpy.events.ConditionValue, None]:
        """Call schedule function when new tasks arrive or old tasks finish."""
        while True:
            triggered = yield self.task_queue.evt_task_arrive | accelerator.evt_task_done
            if self.task_queue.evt_task_arrive in triggered:
                self.task_log.extend(triggered[self.task_queue.evt_task_arrive])
                self.task_queue.acknowledge_task_arrive()
            if accelerator.evt_task_done in triggered:
                task = triggered[accelerator.evt_task_done]
                self.task_queue.update_dependency(done=task)
                accelerator.acknowledge_task_done()
            self.schedule(accelerator)

    def schedule(self, accelerator: Accelerator) -> None:
        """Schedule tasks on the accelerator and return a list of tasks that are scheduled."""
        # list of tasks that are scheduled
        tasks_scheduled = []

        # Search all tasks in the task queue
        for task in self.task_queue.q:
            # Skip the task if it still has dependencies
            if len(task.deps) != 0:
                continue

            # Get app_config candidates from an app_pool
            app_config_list = self.app_pool.get(task.app)
            # Skip the task if there is no possible app config
            if len(app_config_list) == 0:
                logger.warning(f"There is no app_config for {task.app} in the app_pool.")
                continue

            # TODO: Optimize by choosing the best bitstream from the app_pool.
            # For now, we just use the first available app_config from the app_pool.
            is_mapped = False
            for app_config in app_config_list:
                prs = accelerator.map(app_config)
                if len(prs) > 0:
                    is_mapped = True
                    break

            # Skip the task if any app_config is not mappable
            if is_mapped is False:
                continue

            # Set app_config for the task
            task.set_app_config(app_config)
            logger.info(f"[@ {self.env.now}] {task.tag} is scheduled.")
            accelerator.execute(task, prs)
            task.ts_schedule = int(self.env.now)
            tasks_scheduled.append(task)

        # Remove tasks that are scheduled from the queue
        for task in tasks_scheduled:
            self.task_queue.remove(task)
