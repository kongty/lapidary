import simpy
import numpy as np
from typing import Optional, TypedDict, Union, Dict, List, Generator
from lapidary.task import Task
from lapidary.kernel import Kernel
from lapidary.scheduler import Scheduler
from lapidary.util.exceptions import DistributionTypeException
from lapidary.util.task_logger import TaskLogger
from enum import Enum
import logging
from collections import defaultdict
logger = logging.getLogger(__name__)


class KernelConfigType(TypedDict):
    app: str
    dependencies: List[str]


class TaskGeneratorConfigType(TypedDict):
    type: str
    start: int
    interval: Union[int, List[int]]
    lambda_: int
    size: int
    kernels: Dict[str, KernelConfigType]


class DistributionType(Enum):
    STREAMING = 0
    POISSON = 1
    FIXED = 2


class TaskGeneratorDistribution:
    def __init__(self) -> None:
        self.type: DistributionType.STREAMING
        self.start = 0
        self.interval: Union[int, List[int]]
        self.lambda_ = 0
        self.size = 0

    def set_distribution(self, config) -> None:
        if config['type'] == 'streaming':
            self.type = DistributionType.STREAMING
            self.start = config['start']
            self.size = config['size']
        elif config['type'] == 'poisson':
            self.type = DistributionType.POISSON
            self.start = config['start']
            self.lambda_ = config['lambda']
            self.size = config['size']
        elif config['type'] == 'fixed':
            self.type = DistributionType.FIXED
            self.start = config['start']
            self.interval = config['interval']
            self.size = config['size']
        else:
            raise DistributionTypeException()


class TaskGenerator:
    def __init__(self, env: simpy.Environment, name: str, config: Optional[TaskGeneratorConfigType],
                 task_logger: TaskLogger = None) -> None:
        self.env = env
        self.name = name
        self.dist = TaskGeneratorDistribution()
        self.kernels: Dict[str, KernelConfigType] = {}
        if config is not None:
            self.set_task_generator(config)
        self.task_logger = task_logger
        self.scheduler: Scheduler

    def set_task_generator(self, config: TaskGeneratorConfigType) -> None:
        """Set task generator properties with input configuration file."""
        self.dist.set_distribution(config['dist'])
        self.kernels = config["kernels"]
        for kernel in self.kernels.values():
            # If dependencies field is empty, make empty list
            if 'dependencies' not in kernel:
                kernel['dependencies'] = []

    def set_scheduler(self, scheduler: Scheduler) -> None:
        """Set a scheduler for each task generator."""
        self.scheduler = scheduler

    def generate(self) -> Generator[simpy.events.Event, None, None]:
        """Generate tasks and put it in a task queue."""
        if self.dist.type == DistributionType.STREAMING:
            self.env.process(self._generate_streaming)
        elif self.dist.type == DistributionType.POISSON:
            self.env.process(self._generate_poisson)
        elif self.dist.type == DistributionType.FIXED:
            self.env.process(self._generate_fixed)
        else:
            raise DistributionTypeException()

    def _create_task(self, id: int) -> Task:
        # Create task
        task = Task(self.name, id, int(self.env.now))
        # Create kernels
        kernels = []
        for kernel_name, kernel_v in self.kernels.items():
            kernel = Kernel(task, kernel_name, kernel_v['app'], kernel_v['dependencies'])
            kernels.append(kernel)
        kernels = self.kernel_topological_sort(kernels)
        task.set_kernels(kernels)
        if self.task_logger is not None:
            self.task_logger.add_task(task)

        return task

    def _generate_streaming(self) -> Generator[simpy.events.Event, None, None]:
        yield self.env.timeout(self.dist.start)
        id = 1
        while True:
            task = self._create_task(id)
            # TODO: Do I need to acquire controller?
            yield self.env.process(self.scheduler.task_queue.put(task))
            yield task.evt_task_done
            id += 1

    def _generate_poisson(self) -> Generator[simpy.events.Event, None, None]:
        # Generate temporary 1000 intervals for poisson distribution and loop this interval if size is larger than 1000
        NUM_INTERVALS = 1000
        intervals = list(np.random.poisson(self.dist.lambda_, NUM_INTERVALS))
        wait_time = 0
        id = 1
        while True:
            if id == 1:
                yield self.env.timeout(self.dist.start)
            else:
                # TODO: Check if this logic is correct or not
                interval = max(intervals[(id - 1) % NUM_INTERVALS] - wait_time, 0)
                yield self.env.timeout(interval)
            task = self._create_task(id)
            logger.info(f"[@ {self.env.now}] {task.tag} is generated.")

            wait_start = int(self.env.now)
            yield self.env.process(self.scheduler.task_queue.put(task))
            wait_end = int(self.env.now)
            wait_time = wait_end - wait_start

            if wait_time > 0:
                logger.warning(f"[@ {self.env.now}] {task.tag} has been blocked for {wait_time}.")

            id += 1

    def _generate_fixed(self) -> Generator[simpy.events.Event, None, None]:
        """Generate tasks and put it in a task queue."""
        wait_time = 0
        id = 1
        while True:
            if id == 1:
                yield self.env.timeout(self.dist.start)
            else:
                # TODO: Check if this logic is correct or not
                interval = max(self.dist.interval - wait_time, 0)
                yield self.env.timeout(interval)
            task = self._create_task(id)
            logger.info(f"[@ {self.env.now}] {task.tag} is generated.")

            wait_start = int(self.env.now)
            yield self.env.process(self.scheduler.task_queue.put(task))
            wait_end = int(self.env.now)
            wait_time = wait_end - wait_start

            if wait_time > 0:
                logger.warning(f"[@ {self.env.now}] {task.tag} has been blocked for {wait_time}.")

            id += 1

    def kernel_topological_sort(self, kernels: List[Kernel]) -> List[Kernel]:
        index_dict = {}
        for i, task in enumerate(kernels):
            index_dict[task.name] = i

        adj_list = defaultdict(list)
        for i, task in enumerate(kernels):
            for adj in task.deps:
                adj_list[i].append(index_dict[adj])

        num_v = len(kernels)
        visited = [False for _ in range(num_v)]
        stack: List[int] = []

        def _topological_sort(v, visited, stack):
            visited[v] = True
            for i in adj_list[v]:
                if visited[i] is False:
                    _topological_sort(i, visited, stack)

            stack.append(v)

        for i in range(num_v):
            if visited[i] is False:
                _topological_sort(i, visited, stack)

        result: List[Kernel] = []
        for i in stack:
            result.append(kernels[i])

        return result
