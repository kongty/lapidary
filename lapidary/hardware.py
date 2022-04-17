from asyncio import Task
from lapidary.architecture import Architecture
import simpy
from typing import List


class Hardware:
    def __init__(self, env: simpy.Environment, architecture: Architecture) -> None:
        self.env = env
        self.architecture = architecture
        self.pr = [0] * self.architecture.num_pr
        # TODO: Handle the case when two tasks are done simultaneously.
        self.evt_task_done = self.env.event()

    def allocate(self, task: Task, pr: List[int]):
        pass

    def execute(self, task):
        yield self.env.process(task.execute())
