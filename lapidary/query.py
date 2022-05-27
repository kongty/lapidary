import simpy
import numpy as np
from typing import Optional, TypedDict, Union, Dict, List, Generator, cast
from lapidary.task import Task
from lapidary.task_queue import TaskQueue
import logging
from collections import defaultdict
logger = logging.getLogger(__name__)


class TaskConfigType(TypedDict):
    app: str
    dependencies: List[str]


class QueryConfigType(TypedDict):
    dist: str
    dist_start: int
    dist_interval: Union[int, List[int]]
    dist_lambda: int
    dist_size: int
    tasks: Dict[str, TaskConfigType]


class Query:
    def __init__(self, env: simpy.Environment, name: str, config: Optional[QueryConfigType]) -> None:
        self.env = env
        self.name = name
        self.dist = 'fixed'
        self.dist_start = 0
        self.dist_interval: Union[int, List[int]]
        self.dist_lambda = 0
        self.dist_size = 0
        self.tasks: Dict[str, TaskConfigType] = {}
        if config is not None:
            self.set_query(config)
        self._intervals = self._generate_intervals()

    def set_query(self, config: QueryConfigType) -> None:
        """Set query properties with input configuration file."""
        self.dist = config['dist']
        self.dist_start = config['dist_start']
        if self.dist == 'fixed':
            self.dist_interval = config['dist_interval']
            self.dist_size = config['dist_size']
        elif self.dist == 'manual':
            self.dist_interval = config['dist_interval']
        elif self.dist == 'poisson':
            self.dist_lambda = config['dist_lambda']
            self.dist_size = config['dist_size']
        self.tasks = config["tasks"]
        for task in self.tasks.values():
            if 'dependencies' not in task:
                task['dependencies'] = []

    def _generate_intervals(self) -> List[int]:
        """Generate an interval list."""
        intervals: List[int] = []
        if self.dist == "fixed":
            if self.dist_size > 0:
                intervals = [self.dist_start] + [cast(int, self.dist_interval) for _ in range(self.dist_size - 1)]
            return intervals
        elif self.dist == "manual":
            intervals = cast(List[int], self.dist_interval)
            return intervals
        elif self.dist == "poisson":
            if self.dist_size > 0:
                intervals = [self.dist_start] + list(np.random.poisson(self.dist_lambda, self.dist_size - 1))
            return intervals
        else:
            error = f"The distribution '{self.dist}' is not supported. ['fixed', 'poission']"
            raise Exception(error)

    def dispatch(self, task_queue: TaskQueue, task_logger: Optional[List[Task]] = None) -> Generator[simpy.events.Event,
                                                                                                     None, None]:
        """Generate tasks and put it in a task queue."""
        wait_time = 0
        for id, interval in enumerate(self._intervals):
            # If a query is blocked longer than its predetermined interval, dispatch right away.
            interval = max(interval, wait_time)
            yield self.env.timeout(interval)
            tasks = []
            task_dict = {}
            # Create tasks
            for task_k, task_v in self.tasks.items():
                task = Task(self.env, self.name, id, task_k, task_v['app'], task_v['dependencies'])
                if task_logger is not None:
                    task_logger.append(task)
                task.ts_dispatch = int(self.env.now)
                task_dict[task_k] = task
                tasks.append(task)
            tasks = self.task_topological_sort(tasks)
            logger.info(f"[@ {self.env.now}] {self.name} #{id} is dispatched.")
            wait_start = self.env.now
            yield self.env.process(task_queue.put(tasks))
            wait_end = self.env.now
            wait_time = int(wait_end) - int(wait_start)
            if wait_time > 0:
                logger.info(f"[@ {self.name} #{id} has been blocked for {wait_time}.")

    def task_topological_sort(self, tasks: List[Task]) -> List[Task]:
        index_dict = {}
        for i, task in enumerate(tasks):
            index_dict[task.name] = i

        adj_list = defaultdict(list)
        for i, task in enumerate(tasks):
            for adj in task.deps:
                adj_list[i].append(index_dict[adj])

        num_v = len(tasks)
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

        result: List[Task] = []
        for i in stack:
            result.append(tasks[i])

        return result
