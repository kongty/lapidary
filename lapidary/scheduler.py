from __future__ import annotations
import simpy
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generator, Any, List
from lapidary.components import PRR, Bank
from lapidary.task_queue import TaskQueue
from lapidary.kernel import Kernel, KernelStatus
from lapidary.app import AppConfig, AppPool, NoAppConfigError
if TYPE_CHECKING:
    from lapidary.accelerator import Accelerator
import logging
logger = logging.getLogger(__name__)


class Scheduler(ABC):
    def __init__(self, env: simpy.Environment) -> None:
        self.env = env
        self.delay = 0
        self.task_queue: TaskQueue
        self.app_pool: AppPool
        self.accelerator: Accelerator
        self.eutmcontroller = simpy.Resource(self.env, capacity=1)

    def set_accelerator(self, accelerator: Accelerator) -> None:
        self.accelerator = accelerator

    def set_app_pool(self, app_pool: AppPool) -> None:
        self.app_pool = app_pool

    def run(self) -> None:
        self.env.process(self.proc_schedule())

    @abstractmethod
    def proc_schedule(self) -> Generator[simpy.events.Event, Any, Any]:
        """Decide when to call scheduler."""
        pass

    @abstractmethod
    def schedule(self) -> Generator[simpy.events.Event, None, None]:
        """Decide how to schedule."""
        pass


class GreedyScheduler(Scheduler):
    def __init__(self, env: simpy.Environment) -> None:
        super().__init__(env)
        self.task_queue = TaskQueue(self.env, maxsize=100)
        self.delay = 1000

    def proc_schedule(self) -> Generator[simpy.events.Event, simpy.events.ConditionValue,
                                         None]:
        """Call schedule function when new tasks arrive or old tasks finish."""
        while True:
            triggered = yield self.task_queue.evt_task_arrive | self.accelerator.evt_kernel_done
            if self.accelerator.evt_kernel_done in triggered:
                kernel, mut_kernel_done = triggered[self.accelerator.evt_kernel_done]
                self.task_queue.update_kernel_done(kernel=kernel)
                self.accelerator.acknowledge_kernel_done(mut_kernel_done)
            try:
                yield self.env.process(self.schedule())
            except simpy.Interrupt:
                # Interrupt when new task arrives while scheduling
                pass

    def schedule(self) -> Generator[simpy.events.Event, None, None]:
        """Schedule tasks on the accelerator and return a list of tasks that are scheduled."""
        logger.info(f"[@ {self.env.now}] Call schedule.")
        kernels = self.select_kernels(accelerator=self.accelerator)
        logger.info(f"[@ {self.env.now}] Number of tasks being scheduled: {len(kernels)}")
        # schedule delay
        yield self.env.timeout(self.delay)

        for kernel in kernels:
            logger.info(f"[@ {self.env.now}] {kernel.tag} is scheduled to prr{list(map(lambda x: x.id, kernel.prrs))}, "
                        f"bank {list(map(lambda x: x.id, kernel.banks))}.")
            yield self.env.process(self.task_queue.remove(kernel))
            kernel.ts_schedule = int(self.env.now)
            # TODO: Change kernel status to RUNNING
            self.accelerator.execute(kernel)

    def select_kernels(self) -> List[Kernel]:
        # list of tasks that are scheduled
        tasks = []

        # Search all tasks in the task queue
        q_tmp = self.task_queue.q.copy()
        for task in q_tmp:
            # Break if the task cannot be mapped.
            if len(task.deps) != 0:
                continue

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
                prrs, banks = self.accelerator.map(app_config)
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

            if is_mapped is False:
                continue

            # Set app_config for the task
            task.set_app_config(selected_app_config)
            self.accelerator.allocate(task, selected_prrs, selected_banks)
            tasks.append(task)

        return tasks
