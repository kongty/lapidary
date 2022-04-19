import simpy
from lapidary.app_pool import AppPool
from lapidary.architecture import Architecture
from lapidary.accelerator import Accelerator
from lapidary.workload import Workload
from lapidary.scheduler import GreedyScheduler


class Lapidary:
    def __init__(self, architecture_filename: str, workload_filename: str, app_pool: AppPool) -> None:
        # simpy environment
        self.env = simpy.Environment()
        self.architecture = Architecture(architecture_filename)
        self.workload = Workload(self.env, workload_filename)
        self.accelerator = Accelerator(self.env, self.architecture)
        self.scheduler = GreedyScheduler(self.env)
        self.app_pool = app_pool

    def run(self, until: int) -> None:
        """Dispatch workload, start scheduler, and run simpy simulation."""
        self.workload.run_dispatch(self.scheduler.task_queue)
        self.scheduler.run(self.accelerator, self.app_pool)

        self.env.run(until=until)
