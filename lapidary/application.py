import simpy
import numpy as np
from typing import Optional, TypedDict, Union, Dict, List, Generator, cast
from lapidary.task import Task
from lapidary.task_queue import TaskQueue
import logging
logger = logging.getLogger(__name__)


class TaskConfigType(TypedDict):
    app: str
    dependencies: List[str]


class ApplicationConfigType(TypedDict):
    dist: str
    dist_start: int
    dist_interval: Union[int, List[int]]
    dist_lambda: int
    dist_size: int
    tasks: Dict[str, TaskConfigType]


class Application:
    def __init__(self, env: simpy.Environment, name: str, config: Optional[ApplicationConfigType]) -> None:
        self.env = env
        self.name = name
        self.dist = 'fixed'
        self.dist_start = 0
        self.dist_interval: Union[int, List[int]]
        self.dist_lambda = 0
        self.dist_size = 0
        self.tasks: Dict[str, TaskConfigType] = {}
        if config is not None:
            self.set_application(config)
        self._intervals = self._generate_intervals()

    def set_application(self, config: ApplicationConfigType) -> None:
        """Set application properties with input configuration file."""
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
        if self.dist == "fixed":
            intervals: List[int] = [cast(int, self.dist_interval) for _ in range(self.dist_size)]
            if len(intervals) > 0:
                intervals[0] += self.dist_start
            return intervals
        elif self.dist == "manual":
            intervals = cast(List[int], self.dist_interval)
            if len(intervals) > 0:
                intervals[0] += self.dist_start
            return intervals
        elif self.dist == "poisson":
            intervals = list(np.random.poisson(self.dist_lambda, self.dist_size))
            if len(intervals) > 0:
                intervals[0] += self.dist_start
            return intervals
        else:
            error = f"The distribution '{self.dist}' is not supported. ['fixed', 'poission']"
            raise Exception(error)

    def run_dispatch(self, task_queue: TaskQueue) -> None:
        """Run dispatch proccess of the application."""
        self.env.process(self.dispatch(task_queue))

    def dispatch(self, task_queue: TaskQueue) -> Generator[simpy.events.Event, None, None]:
        """Generate tasks and put it in a task queue."""
        for id, interval in enumerate(self._intervals):
            yield self.env.timeout(interval)

            tasks = []
            for task_k, task_v in self.tasks.items():
                task = Task(self.env, self.name, id, task_k, task_v['app'], task_v['dependencies'])
                tasks.append(task)
            task_queue.put(tasks)
            logger.info(f"[@ {self.env.now}] {self.name} #{id} arrived.")
