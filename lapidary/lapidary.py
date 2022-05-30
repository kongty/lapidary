import simpy
from lapidary.app import AppPool
from lapidary.accelerator import Accelerator, AcceleratorConfigType
from lapidary.workload import Workload
from lapidary.scheduler import GreedyScheduler
from typing import Optional, Union, Dict
from util.logger import Logger


class Lapidary:
    def __init__(self, accelerator_config: Optional[Union[str, AcceleratorConfigType]],
                 workload_config: Optional[Union[str, Dict]], app_pool: AppPool) -> None:
        # simpy environment
        self.env = simpy.Environment()
        self.workload = Workload(self.env, workload_config)
        self.accelerator = Accelerator(self.env, accelerator_config)
        self.app_pool = app_pool
        self.scheduler = GreedyScheduler(self.env)
        self.scheduler.set_app_pool(self.app_pool)
        self.task_logger = Logger()
        self.set_interface()

    def run(self, until: int) -> None:
        """Dispatch workload, start scheduler, and run simpy simulation."""
        self.workload.run_dispatch(self.task_logger)
        self.scheduler.run(self.accelerator)
        self.env.run(until=until)

    def set_interface(self) -> None:
        self.workload.set_task_queue(self.scheduler.task_queue)

    def dump_log(self, filename: str) -> None:
        self.task_logger.dump_task_df(filename)
