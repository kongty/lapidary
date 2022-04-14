from lapidary.hardware import Hardware
from lapidary.architecture import Architecture
from lapidary.workload import Workload
from lapidary.dispatcher import Dispatcher
import simpy


class Simulator:
    def __init__(self, architecture: Architecture, workload: Workload) -> None:
        # simpy environment
        self.env = simpy.Environment()

        self.hardware = Hardware(architecture)
        self.workload = workload
        self.dispatcher = Dispatcher(self.env, self.workload)
        self.scheduler = "greedy"

    def run(self) -> None:
        self.env.run()
