from __future__ import annotations
import simpy
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generator, Any, List, Optional, Tuple
from lapidary.components import PRR, Bank
from lapidary.task_queue import TaskQueue
from lapidary.kernel import Kernel, KernelStatus
from lapidary.app import AppConfig, AppPool
from lapidary.util.exceptions import NoAppConfigException
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
        self.mut_controller = simpy.Resource(self.env, capacity=1)

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


class FCFSScheduler(Scheduler):
    def __init__(self, env: simpy.Environment) -> None:
        super().__init__(env)
        self.task_queue = TaskQueue(self.env, maxsize=100)
        self.delay = 100

    def proc_schedule(self) -> Generator[simpy.events.Event, simpy.events.ConditionValue,
                                         None]:
        """Call schedule function when new tasks arrive or old tasks finish."""
        while True:
            triggered = yield self.task_queue.evt_task_arrive | self.accelerator.evt_kernel_done
            if self.accelerator.evt_kernel_done in triggered:
                kernel, mut_kernel_done = triggered[self.accelerator.evt_kernel_done]
                yield self.env.process(self.task_queue.update_kernel_done(kernel=kernel))
                self.accelerator.acknowledge_kernel_done(mut_kernel_done)
            try:
                yield self.env.process(self.schedule())
            except simpy.Interrupt:
                # Interrupt when new task arrives while scheduling
                pass

    def schedule(self) -> Generator[simpy.events.Event, None, None]:
        """Schedule kernels on the accelerator and return a list of kernels that are scheduled."""

        # If there is no ready kernel, just pass
        if len(self.task_queue.get_ready_kernels()) == 0:
            return

        logger.debug(f"[@ {self.env.now}] Call schedule.")
        # schedule delay
        yield self.env.timeout(self.delay)

        # Select kernels to run
        kernels = self.select_kernels()
        logger.debug(f"[@ {self.env.now}] Number of tasks being scheduled: {len(kernels)}")

        for kernel in kernels:
            logger.debug(f"[@ {self.env.now}] {kernel.tag} is scheduled to prr{list(map(lambda x: x.id, kernel.prrs))},"
                         f" bank {list(map(lambda x: x.id, kernel.banks))}.")
            self.task_queue.update_kernel_scheduled(kernel=kernel)
            self.accelerator.execute(kernel)

    def select_kernels(self) -> List[Kernel]:
        # selected kernels list
        kernels = []

        # Search kernels in the ready_kernels queue
        for kernel in self.task_queue.get_ready_kernels():
            app_config, prrs, banks = self.select_app_config(kernel)

            # If map is not available, then continue
            if app_config is None:
                continue
            # Set app_config for the task
            kernel.set_app_config(app_config)
            self.accelerator.allocate(kernel, prrs, banks)
            kernels.append(kernel)

        return kernels

    def select_app_config(self, kernel: Kernel) -> Tuple[Optional[AppConfig], List[PRR], List[Bank]]:
        """
        TODO:
        For now, we select app_config, and hardware resources in the same function. It can be changed in the future.
        e.g. First select the amount of resources and then dataflow.
        """
        # Get app_config candidates from an app_pool
        app_config_list = self.app_pool.get(kernel.app)

        # Raise an error if there is no possible app config
        if len(app_config_list) == 0:
            raise NoAppConfigException(f"There is no app_config for {kernel.app} in the app_pool.")

        # TODO: Implement how to choose best target app from app_pool
        # For now, we just use the first available app_config from the app_pool.
        runtime = 0
        selected_app_config: Optional[AppConfig] = None
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

        return selected_app_config, selected_prrs, selected_banks
