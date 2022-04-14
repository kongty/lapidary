from lapidary.architecture import Architecture
from lapidary.workload import Workload


class Simulator:
    def __init__(self, architecture: Architecture, workload: Workload) -> None:
        self.architecture = architecture
        self.workload = workload
        self.scheduler = "greedy"

    def run(self) -> None:
        pass
