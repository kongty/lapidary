import simpy
from lapidary.task import Task
from typing import Union, List, Optional


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
        for task in tasks:
            self._put(task)
        self.evt_task_arrive.succeed(value=tasks)

    def _put(self, task: Task) -> None:
        # Filter a duplicate task in the queue.
        if task not in self.q:
            self.q.append(task)

    def peek(self, idx: int = 0) -> Task:
        return self.q[idx]

    def get(self, task: Optional[Task]) -> Task:
        if task is None:
            result = self.q.pop(0)
        elif task in self.q:
            result = task
            self.q.remove(task)
        else:
            raise Exception(f"{task.tag} is not in the queue.")
        return result

    def remove(self, task: Task) -> None:
        self.q.remove(task)

    def size(self) -> int:
        return len(self.q)

    def acknowledge_task_arrive(self) -> None:
        self.evt_task_arrive = self.env.event()

    def update_dependency(self, done: Task) -> None:
        for task in self.q:
            if (done.name in task.deps
                and task.workload_name == done.workload_name
                    and task.workload_id == done.workload_id):
                task.deps.remove(done.name)
