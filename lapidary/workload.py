import os
import yaml
import simpy
import numpy as np
from typing import Optional, TypedDict, Union, Dict, List, Generator
from lapidary.task import Task
from lapidary.task_queue import TaskQueue
import logging
logger = logging.getLogger(__name__)


class TaskConfigType(TypedDict):
    app: str
    dependencies: List[str]


class WorkloadConfigType(TypedDict):
    dist: str
    dist_start: int
    dist_interval: List[int]
    dist_lambda: int
    dist_size: int
    tasks: Dict[str, TaskConfigType]


class Workload:
    def __init__(self, env: simpy.Environment, config: Optional[Union[str, Dict[str, WorkloadConfigType]]] = None) -> None:
        self.env = env
        self.name = 'workload_0'
        self.dist = 'manual'
        self.dist_start = 0
        self.dist_interval: List[int]
        self.dist_lambda = 0
        self.dist_size = 0
        self.tasks: Dict[str, TaskConfigType] = {}
        if config is not None:
            self.set_workload(config)
        self._intervals = self._generate_intervals()

    def set_workload(self, config: Union[str, Dict[str, WorkloadConfigType]]) -> None:
        """Set workload properties with input configuration file."""
        if isinstance(config, str):
            config = os.path.realpath(config)
            if not os.path.exists(config):
                raise Exception("[ERROR] Workload config file not found")
            else:
                logger.info(f"Workload config file read: {config}")

            with open(config, 'r') as f:
                config_dict = yaml.load(f, Loader=yaml.loader.SafeLoader)
        else:
            config_dict = config

        assert len(config_dict) == 1, "It only supports one workload for now."
        for k, v in config_dict.items():
            self.name = k
            self.dist = v['dist']
            self.dist_start = v['dist_start']
            if self.dist == 'manual':
                self.dist_interval = v['dist_interval']
            elif self.dist == 'poisson':
                self.dist_lambda = v['dist_lambda']
                self.dist_size = v['dist_size']
            self.tasks = v["tasks"]
            for task in self.tasks.values():
                if 'dependencies' not in task:
                    task['dependencies'] = []

    def _generate_intervals(self) -> List[int]:
        """Generate an interval list."""
        if self.dist == "manual":
            intervals = self.dist_interval
            if len(intervals) > 0:
                intervals[0] += self.dist_start
            return intervals
        elif self.dist == "poisson":
            intervals = list(np.random.poisson(self.dist_lambda, self.dist_size))
            if len(intervals) > 0:
                intervals[0] += self.dist_start
            return intervals
        else:
            error = f"The distribution '{self.dist}' is not supported. ['manual', 'poission']"
            raise Exception(error)

    def run_dispatch(self, task_queue: TaskQueue) -> None:
        """Run dispatch proccess of the workload."""
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
