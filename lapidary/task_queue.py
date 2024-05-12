import simpy
from lapidary.kernel import KernelStatus
from lapidary.task import Task
from lapidary.kernel import Kernel
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

        self._controller = simpy.Resource(self.env, capacity=1)

    def __getitem__(self, key: int) -> Task:
        return self.q[key]

    @property
    def size(self) -> int:
        return len(self.q)

    @property
    def full(self) -> bool:
        return self.maxsize == len(self.q)

    def put(self, task: Task) -> Generator[simpy.events.Event, None, None]:
        yield self._q.put(amount=1)
        self.q.append(task)
        task.timestamp.queue = int(self.env.now)
        logger.debug(f"[@ {self.env.now}] {task.tag} is added to a task queue.")

        self.evt_task_arrive.succeed(value=task)
        self.evt_task_arrive = self.env.event()

    def get_ready_kernels(self) -> List[Kernel]:
        ready_kernels = []
        for task in self.q:
            ready_kernels += task.ready_kernels
        return ready_kernels

    def remove(self, task: Task) -> Generator[simpy.events.Event, None, None]:
        logger.debug(f"[@ {self.env.now}] {task.tag} is removed from a queue.")
        self.q.remove(task)
        yield self._q.get(amount=1)

    def update_kernel_done(self, kernel: Kernel) -> Generator[simpy.events.Event, None, None]:
        # kernel status update
        kernel.status = KernelStatus.DONE
        # dependency update
        task = kernel.task
        task.update_dependency(kernel)
        if len(task.pending_kernels) == 0:
            yield self.env.process(self.remove(task))
            task.timestamp.done = int(self.env.now)
            task.evt_task_done.succeed()

    def update_kernel_scheduled(self, kernel: Kernel) -> None:
        # timestamp update
        kernel.timestamp.schedule = int(self.env.now)
        kernel.task.timestamp.schedule = min(int(self.env.now), kernel.task.timestamp.schedule)
        # kernel status update
        kernel.status = KernelStatus.RUNNING
        # task next kernel_idx update
        kernel.task.next_kernel_idx += 1
