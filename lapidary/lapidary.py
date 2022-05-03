import simpy
import os
from pathlib import Path
from lapidary.app import AppPool
from lapidary.accelerator import Accelerator, AcceleratorConfigType
from lapidary.workload import Workload
from lapidary.scheduler import GreedyScheduler
from lapidary.task import Task
from typing import Optional, Union, Dict, List
import logging
logger = logging.getLogger(__name__)


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
        self.task_logger: List[Task] = []

    def run(self, until: int) -> None:
        """Dispatch workload, start scheduler, and run simpy simulation."""
        self.workload.run_dispatch(self.scheduler.task_queue, self.task_logger)
        self.scheduler.run(self.accelerator)
        self.env.run(until=until)

    def generate_log(self, filename: str) -> None:
        filename = os.path.realpath(filename)
        Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)
        with open(filename, 'w') as f:
            header = 'tag, ts_dispatch, ts_queue, ts_schedule, ts_done\n'
            f.write(header)
            for task in self.task_logger:
                log = f"{task.tag}, "
                log += f"{task.ts_dispatch}, "
                log += f"{task.ts_queue}, "
                log += f"{task.ts_schedule}, "
                log += f"{task.ts_done}\n"
                f.write(log)
        logger.info(f"A log file was generated: {filename}")
