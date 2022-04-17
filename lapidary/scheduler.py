import simpy
from abc import ABC, abstractmethod
from lapidary.hardware import Hardware
from lapidary.task import Task
from lapidary.task_queue import TaskQueue
from lapidary.app_pool import AppPool
from typing import List


class Scheduler(ABC):
    def __init__(self, env: simpy.Environment, app_pool: AppPool) -> None:
        self.env = env
        self.app_pool = app_pool
        self.task_queue = TaskQueue(self.env)

    def run(self, hardware: Hardware) -> None:
        self.env.process(self.run_schedule(hardware))

    @abstractmethod
    def run_schedule(self, hardware: Hardware) -> None:
        pass

    @abstractmethod
    def schedule(self) -> None:
        pass


class GreedyScheduler(Scheduler):
    def __init__(self, env: simpy.Environment, app_pool: AppPool) -> None:
        super().__init__(env, app_pool)

    def run_schedule(self, hardware: Hardware) -> None:
        """Call schedule function when new tasks arrive or pre-existing tasks finish."""
        while True:
            yield self.task_queue.evt_task_arrive
            for _ in range(self.task_queue.size()):
                task = self.task_queue.get()
                self.schedule([task], hardware)
                print(f"{task.name} is scheduled @ {self.env.now}")

    def schedule(self, tasks: List[Task], hardware: Hardware) -> None:
        """Schedule tasks on hardware."""
        pass
