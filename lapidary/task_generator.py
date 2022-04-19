import simpy
import numpy as np
from typing import List
from lapidary.task import Task
from lapidary.task_queue import TaskQueue


class TaskGenerator:
    def __init__(self, env: simpy.Environment, config_dict: dict) -> None:
        self.env = env
        self.name = 'task_0'
        self.app = 'app_0'
        self.dist = 'manual'
        self.dist_start = 0
        self.dist_time = []
        self.dist_size = 0
        self.dist_lam = 0
        self._set_params(config_dict)
        self.intervals = self._generate_intervals()

    def _set_params(self, config_dict: dict) -> None:
        """Set properties."""
        self.name = config_dict['name']
        self.app = config_dict['app']
        self.dist = config_dict['dist']
        self.dist_start = config_dict['dist_start']
        if self.dist == 'manual':
            self.dist_interval = config_dict['dist_interval']
        elif self.dist == 'poisson':
            self.dist_lam = config_dict['dist_lam']
            self.dist_size = config_dict['dist_size']

    def _generate_intervals(self) -> List[int]:
        """Generate a interval list."""
        if self.dist == "manual":
            dist_interval = self.dist_interval
            if len(dist_interval) > 0:
                dist_interval[0] += self.dist_start
            return dist_interval
        elif self.dist == "poisson":
            dist_interval = list(np.random.poisson(self.dist_lam, self.dist_size))
            if len(dist_interval) > 0:
                dist_interval[0] += self.dist_start
            return dist_interval
        else:
            error = f"The distribution '{self.dist}' is not supported. ['manual', 'poission']"
            raise Exception(error)

    def proc_generate(self, task_queue: TaskQueue) -> None:
        """Generate a task and put to a task_queue in a scheduler."""
        for task_id, interval in enumerate(self.intervals):
            self.evt_generate = self.env.event()
            yield self.env.timeout(interval)

            task = Task(self.env, self.name, task_id, self.app)
            task.ts_arrive = self.env.now
            self.evt_generate.succeed(value=task)
            print(f"[@ {self.env.now}] {task.name} arrived.")

            task_queue.put(task)
