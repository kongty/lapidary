from lapidary.workload import Workload
import simpy


class Dispatcher:
    def __init__(self, env: simpy.Environment, workload: Workload) -> None:
        self.workload = workload
