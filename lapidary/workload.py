import os
import yaml
import simpy
import numpy as np
from typing import Optional, Union, Dict, List
from lapidary.task import Task
from lapidary.task_queue import TaskQueue


class Workload:
    def __init__(self, env: simpy.Environment, config: Optional[Union[str, Dict]] = None) -> None:
        self.env = env
        self.name = 'workload_0'
        self.dist = 'manual'
        self.dist_start = 0
        self.dist_interval = []
        self.dist_lambda = 0
        self.dist_size = 0
        self.tasks = []
        if config is not None:
            self.set_workload(config)
        self._intervals = self._generate_intervals()

    def set_workload(self, config: Union[str, Dict]) -> None:
        """Set workload properties with input configuration file."""
        if type(config) is str:
            config = os.path.realpath(config)
            if not os.path.exists(config):
                raise Exception("[ERROR] Workload config file not found")
            else:
                print(f"[LOG] Workload config file read: {config}")
            with open(config, 'r') as f:
                config = yaml.load(f, Loader=yaml.loader.SafeLoader)
        assert len(config) == 1, "It only supports one workload for now."
        for k, v in config.items():
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
        """Generate a interval list."""
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

    def dispatch(self, task_queue: TaskQueue):
        """Generate tasks and put it in a task queue."""
        for id, interval in enumerate(self._intervals):
            yield self.env.timeout(interval)

            tasks = []
            for task_k, task_v in self.tasks.items():
                task = Task(self.env, self.name, id, task_k, task_v['app'], task_v['dependencies'])
                tasks.append(task)
            task_queue.put(tasks)
            print(f"[@ {self.env.now}] {self.name} #{id} arrived.")
