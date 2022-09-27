import simpy
from lapidary.workload import Workload


class Host:
    def __init__(self, env: simpy.Environment) -> None:
        self.workload = Workload(self.env, workload_config)
