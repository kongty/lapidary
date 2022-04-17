import simpy
from abc import ABC, abstractmethod
from lapidary.hardware import Hardware
from lapidary.task import Task
from lapidary.task_queue import TaskQueue
from lapidary.app_pool import AppPool
from typing import List


class Scheduler(ABC):
    def __init__(self, env: simpy.Environment) -> None:
        self.env = env
        self.task_queue = TaskQueue(self.env)

    def run(self, hardware: Hardware, app_pool: AppPool) -> None:
        self.env.process(self.run_schedule(hardware, app_pool))

    @abstractmethod
    def run_schedule(self, hardware: Hardware, app_pool: AppPool) -> None:
        pass

    @abstractmethod
    def schedule(self, tasks: List[Task], hardware: Hardware, app_pool: AppPool) -> bool:
        pass


class GreedyScheduler(Scheduler):
    def __init__(self, env: simpy.Environment) -> None:
        super().__init__(env)

    def run_schedule(self, hardware: Hardware, app_pool: AppPool) -> None:
        """Call schedule function when new tasks arrive or pre-existing tasks finish."""
        while True:
            # TODO: Add another event when a task execution finishes.
            yield self.task_queue.evt_task_arrive
            for _ in range(self.task_queue.size()):
                # Get one task from a queue and schedule it on the hardware.
                task = self.task_queue.get()
                self.schedule([task], hardware, app_pool)
                print(f"{task.name} is scheduled @ {self.env.now}")

    def schedule(self, tasks: List[Task], hardware: Hardware, app_pool: AppPool) -> bool:
        """Schedule tasks on hardware and returns True/False if scheduling succeeds/fails."""
