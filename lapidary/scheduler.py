import simpy
from abc import ABC, abstractmethod
from lapidary.workload import Workload


class Scheduler(ABC):
    def __init__(self, env: simpy.Environment, workload: Workload) -> None:
        self.env = env
        self.workload = workload

    @abstractmethod
    def schedule(self):
        pass


class GreedyScheduler(Scheduler):
    def schedule(self):
        while True:
            task = yield self.workload.dispatch_proc
            print(task)
