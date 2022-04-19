import simpy
from lapidary.task import Task
from typing import Union, List


class TaskQueue:
    def __init__(self, env: simpy.Environment) -> None:
        self.env = env
        self.q = []
        self.evt_task_arrive = self.env.event()

    def __getitem__(self, key: int) -> Task:
        return self.q[key]

    def put(self, tasks: Union[Task, List[Task]]) -> None:
        if type(tasks) is Task:
            tasks = [tasks]

        self.q.extend(tasks)
        self.evt_task_arrive.succeed(value=tasks)

    def peek(self, idx: int = 0) -> Task:
        return self.q[idx]

    def get(self) -> Task:
        task = self.q.pop(0)
        return task

    def size(self) -> int:
        return len(self.q)

    def acknowledge(self) -> None:
        self.evt_task_arrive = self.env.event()
