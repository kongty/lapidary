from lapidary.architecture import Architecture
from lapidary.workload import Workload
from lapidary.simulator import Simulator


class Lapidary:
    def __init__(self, architecture_filename: str = None, workload_filename: str = None) -> None:
        self.architecture = Architecture()
        self.workload = Workload()
        if architecture_filename is not None:
            self.set_architecture(architecture_filename)
        if workload_filename is not None:
            self.set_workload(workload_filename)

        self.simulator = Simulator(self.architecture, self.workload)

    def set_architecture(self, architecture_filename: str) -> None:
        self.architecture.read_config_file(architecture_filename)

    def set_workload(self, workload_filename: str) -> None:
        self.workload.read_config_file(workload_filename)

    def run(self) -> None:
        print(self.simulator.workload.name)
