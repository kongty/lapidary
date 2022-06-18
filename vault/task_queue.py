import simpy
from vault.task import Task
from typing import Union, List, Optional, Generator
import logging
logger = logging.getLogger(__name__)


class TaskQueue:
    def __init__(self, env: simpy.Environment, maxsize: int) -> None:
        self.env = env
        self.q: List[Task] = []
        self.maxsize = maxsize
        self._q = simpy.Container(self.env, init=0, capacity=self.maxsize)  # simpy container
        self.evt_task_arrive = self.env.event()
        self.evt_task_arrive_ack = self.env.event()

        self.task_removed: List[Task] = []
        self._controller = simpy.Resource(self.env, capacity=1)

    def __getitem__(self, key: int) -> Task:
        return self.q[key]

    @property
    def size(self) -> int:
        return len(self.q)

    @property
    def full(self) -> bool:
        return self.maxsize == len(self.q)

    def put(self, tasks: Union[Task, List[Task]]) -> Generator[simpy.events.Event, None, List[Task]]:
        if isinstance(tasks, Task):
            tasks = [tasks]
        if len(tasks) > self.maxsize:
            raise Exception(f"A task queue size must be equal to or bigger than {len(tasks)}.")
        yield self._q.put(amount=len(tasks))
        for task in tasks:
            self.q.append(task)
            task.ts_queue = int(self.env.now)
            logger.info(f"[@ {self.env.now}] {task.tag} is added to a queue.")

        self.evt_task_arrive.succeed(value=tasks)
        self.evt_task_arrive = self.env.event()

        return tasks

    def peek(self, idx: int = 0) -> Task:
        return self.q[idx]

    def get(self, task: Optional[Task] = None) -> Generator[simpy.events.Event, None, Task]:
        if task is None:
            yield self.env.process(self._get())
            result = self.q.pop(0)
        elif task in self.q:
            result = task
            yield self.env.process(self._get())
            self.q.remove(task)
        else:
            raise Exception(f"{task.tag} is not in the queue.")
        return result

    def _get(self) -> Generator[simpy.events.Event, None, None]:
        yield self._q.get(amount=1)

    def remove(self, task: Task) -> Generator[simpy.events.Event, None, None]:
        logger.info(f"[@ {self.env.now}] {task.tag} is removed from a queue.")
        self.q.remove(task)
        self.task_removed.append(task)
        yield self.env.process(self._get())

    def update_dependency(self, done: Task) -> None:
        for task in self.q:
            if (done.name in task.deps
                and task.query_name == done.query_name
                    and task.query_id == done.query_id):
                task.deps.remove(done.name)
