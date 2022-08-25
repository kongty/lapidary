import simpy
from vault.app import AppPool
from vault.accelerator import Accelerator, AcceleratorConfigType
from vault.workload import Workload
from vault.scheduler import GreedyScheduler
from typing import Optional, Union, Dict
import os
from util.logger import Logger
import logging
logger = logging.getLogger(__name__)


class Vault:
    def __init__(self, accelerator_config: Optional[Union[str, AcceleratorConfigType]],
                 workload_config: Optional[Union[str, Dict]], app_pool: AppPool) -> None:
        # simpy environment
        self.env = simpy.Environment()
        self.workload = Workload(self.env, workload_config)
        self.accelerator = Accelerator(self.env, accelerator_config)
        self.app_pool = app_pool
        self.scheduler = GreedyScheduler(self.env)
        self.scheduler.set_app_pool(self.app_pool)
        self.task_logger = Logger(self.accelerator.config.num_prr_height * self.accelerator.config.num_prr_width)
        self.set_interface()

    def run(self, until: int) -> None:
        """Dispatch workload, start scheduler, and run simpy simulation."""
        self.workload.run_dispatch(self.task_logger)
        self.scheduler.run(self.accelerator)
        self.env.run(until=until)
        self.task_logger.update_df()
        logger.info(f"ANTT: {self.task_logger.calculate_antt()}")
        logger.info(f"STP: {self.task_logger.calculate_stp()}")
        logger.info(f"Total utilization: {self.task_logger.calculate_utilization()}")

    def set_interface(self) -> None:
        self.workload.set_task_queue(self.scheduler.task_queue)

    def dump_logs(self, dir: str) -> None:
        dir = os.path.realpath(dir)
        if not os.path.exists(dir):
            os.makedirs(dir)

        self.task_logger.update_df()
        self.task_logger.dump_task_df(os.path.join(dir, "task.csv"))
        self.task_logger.dump_perf(os.path.join(dir, "perf.txt"))
