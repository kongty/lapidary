from lapidary.hardware import Hardware
from lapidary.workload import Workload


class Simulator:
    def __init__(self, hardware: Hardware, workload: Workload) -> None:
        self.hardware = hardware
        self.workload = workload
        self.scheduler = "greedy"

    def run(self) -> None:
        pass
