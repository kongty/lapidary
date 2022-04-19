import simpy
from lapidary.app import AppPool
from lapidary.accelerator import Accelerator
from lapidary.workload import Workload
from lapidary.scheduler import GreedyScheduler
from typing import Optional, Union, Dict


class Lapidary:
    def __init__(self, accelerator_config: Optional[Union[str, Dict]], workload_config: Optional[Union[str, Dict]],
                 app_pool: AppPool) -> None:
        # simpy environment
        self.env = simpy.Environment()
        self.workload = Workload(self.env, workload_config)
        self.accelerator = Accelerator(self.env, accelerator_config)
        self.app_pool = app_pool
        self.scheduler = GreedyScheduler(self.env)
        self.scheduler.set_app_pool(self.app_pool)

    def run(self, until: int) -> None:
        """Dispatch workload, start scheduler, and run simpy simulation."""
        self.workload.run_dispatch(self.scheduler.task_queue)
        self.scheduler.run(self.accelerator)

        self.env.run(until=until)
