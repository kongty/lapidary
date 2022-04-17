import simpy
from typing import Optional
from lapidary.architecture import Architecture
from lapidary.hardware import Hardware
from lapidary.workload import Workload
from lapidary.scheduler import GreedyScheduler
from lapidary.simulator import Simulator


class Lapidary:
    def __init__(self, architecture_filename: Optional[str] = None, workload_filename: Optional[str] = None) -> None:
        # simpy environment
        self.env = simpy.Environment()

        self.architecture = Architecture(architecture_filename)
        self.workload = Workload(self.env, workload_filename)
        self.hardware = Hardware(self.env, self.architecture)
        self.scheduler = GreedyScheduler(self.env)
        self.simulator = Simulator(self.env, self.hardware, self.workload, self.scheduler)

    def set_architecture(self, architecture_filename: str) -> None:
        self.architecture = Architecture(architecture_filename)

    def set_workload(self, workload_filename: str) -> None:
        self.workload = Workload(workload_filename)

    def run(self, until: int) -> None:
        self.simulator.run(until=until)
