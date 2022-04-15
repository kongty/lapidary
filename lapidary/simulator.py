from lapidary.hardware import Hardware
from lapidary.workload import Workload
import simpy


class Simulator:
    def __init__(self, env: simpy.Environment, hardware: Hardware, workload: Workload) -> None:
        self.env = env
        self.hardware = hardware
        self.workload = workload
        self.scheduler = "greedy"

    def run(self, until: int) -> None:
        # self.workload.start()
        self.env.run(until=until)
