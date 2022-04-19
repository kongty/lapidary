import simpy
from typing import Optional
from lapidary.app_pool import AppPool
from lapidary.architecture import Architecture
from lapidary.accelerator import Accelerator
from lapidary.workload import Workload
from lapidary.scheduler import GreedyScheduler
from lapidary.simulator import Simulator


class Lapidary:
    def __init__(self, architecture_filename: str, workload_filename: str, app_pool: AppPool) -> None:
        # simpy environment
        self.env = simpy.Environment()
        self.architecture = Architecture(architecture_filename)
        self.workload = Workload(self.env, workload_filename)
        self.accelerator = Accelerator(self.env, self.architecture)
        self.scheduler = GreedyScheduler(self.env)
        self.app_pool = app_pool
        self.simulator = Simulator(self.env, self.accelerator, self.workload, self.scheduler, self.app_pool)

    def run(self, until: int) -> None:
        """Run simulator until 'until' time unit."""
        self.simulator.run(until=until)
