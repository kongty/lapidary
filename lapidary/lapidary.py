import simpy
from lapidary.app import AppPool
from lapidary.accelerator import Accelerator, AcceleratorConfigType
from lapidary.workload import Workload
from lapidary.scheduler import GreedyScheduler
from lapidary.util.task_logger import TaskLogger
from typing import Optional, Union, Dict
import os
import logging
logger = logging.getLogger(__name__)


class Lapidary:
    def __init__(self, accelerator_config: Optional[Union[str, AcceleratorConfigType]],
                 workload_config: Optional[Union[str, Dict]], app_pool: AppPool) -> None:
        # simpy environment
        self.env = simpy.Environment()

        self.accelerator = Accelerator(self.env, accelerator_config)
        # TODO: Get rid of num_prr argument from tasklogger
        self.task_logger = TaskLogger(self.accelerator.config.num_prr_height * self.accelerator.config.num_prr_width)
        self.scheduler = GreedyScheduler(self.env)
        self.app_pool = app_pool
        self.workload = Workload(self.env, workload_config, self.task_logger)

        # Set app pool that scheduler can use
        self.scheduler.set_app_pool(self.app_pool)

        # TODO: Make accelerator system class and move scheduler inside the accelerator system
        # Set accelerator that scheduler can use
        self.scheduler.set_accelerator(self.accelerator)
        self.accelerator.set_scheduler(self.scheduler)

        # Set target scheduler for workload
        self.workload.set_scheduler(self.scheduler)

    def run(self, until: Optional[int] = None) -> None:
        """Dispatch workload, start scheduler, and run simpy simulation."""
        self.workload.run_generate()
        self.scheduler.run()
        self.env.run(until=until)

    def dump_logs(self, dir: str) -> None:
        self.task_logger.post_process()

        dir = os.path.realpath(dir)
        if not os.path.exists(dir):
            os.makedirs(dir)

        self.task_logger.dump_task_df(os.path.join(dir, "task.csv"))
        self.task_logger.dump_kernel_df(os.path.join(dir, "kernel.csv"))
        self.task_logger.dump_perf(os.path.join(dir, "perf.txt"))

        logger.info(f"Tail latency: {self.task_logger.tail_latency}")
        # logger.info(f"ANTT: {self.task_logger.antt}")
        # logger.info(f"STP: {self.task_logger.stp}")
        # logger.info(f"Total utilization: {self.task_logger.utilization}")
