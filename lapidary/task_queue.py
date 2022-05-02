import simpy
from lapidary.task import Task
from typing import Union, List, Optional, Generator
import logging
logger = logging.getLogger(__name__)


class TaskQueue:
    def __init__(self, env: simpy.Environment, maxsize: int) -> None:
        self.env = env
        self.maxsize = maxsize
        self.q: List[Task] = []
        self._q = simpy.Container(self.env, init=0, capacity=self.maxsize)  # simpy container
        self.evt_task_arrive = self.env.event()
        self.evt_task_arrive_ack = self.env.event()

        self._controller = simpy.Resource(self.env, capacity=1)

    def __getitem__(self, key: int) -> Task:
        return self.q[key]

    @property
    def size(self) -> int:
        return len(self.q)

    def put(self, tasks: Union[Task, List[Task]]) -> Generator[simpy.events.Event, None, List[Task]]:
        if isinstance(tasks, Task):
            tasks = [tasks]
        for task in tasks:
            yield self.env.process(self._put(task))
        return tasks

    def _put(self, task: Task) -> Generator[simpy.events.Event, None, None]:
        # Filter a duplicate task in the queue.
        if task not in self.q:
            yield self._q.put(amount=1)
            logger.info(f"[@ {self.env.now}] {task.tag} is added to a queue.")
            self.q.append(task)
            with self._controller.request() as req:
                yield req
                self.evt_task_arrive.succeed(value=task)
                yield self.evt_task_arrive_ack
                self.evt_task_arrive_ack = self.env.event()

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
        yield self.env.process(self._get())
        self.q.remove(task)

    def acknowledge_task_arrive(self) -> None:
        self.evt_task_arrive = self.env.event()
        self.evt_task_arrive_ack.succeed()

    def update_dependency(self, done: Task) -> None:
        for task in self.q:
            if (done.name in task.deps
                and task.query_name == done.query_name
                    and task.query_id == done.query_id):
                task.deps.remove(done.name)
