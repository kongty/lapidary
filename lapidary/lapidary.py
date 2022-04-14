from typing import Optional
from lapidary.architecture import Architecture
from lapidary.workload import Workload
from lapidary.simulator import Simulator


class Lapidary:
    def __init__(self, architecture_filename: Optional[str] = None, workload_filename: Optional[str] = None) -> None:
        self.architecture = Architecture(architecture_filename)
        self.workload = Workload(workload_filename)
        self.simulator = Simulator(self.architecture, self.workload)

    def set_architecture(self, architecture_filename: str) -> None:
        self.architecture = Architecture(architecture_filename)

    def set_workload(self, workload_filename: str) -> None:
        self.workload = Workload(workload_filename)

    def run(self) -> None:
        print(self.simulator.workload.name)
