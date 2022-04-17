import simpy
import numpy as np
from typing import List
from lapidary.task import Task
from lapidary.task_generator_config import TaskGeneratorConfig
from lapidary.task_queue import TaskQueue


class TaskGenerator:
    def __init__(self, env: simpy.Environment, config: TaskGeneratorConfig) -> None:
        self.env = env
        self.done = False
        self.config = config
        self.intervals = self._generate_intervals()

    def _generate_intervals(self) -> List[int]:
        if self.config.dist == "manual":
            dist_interval = self.config.dist_interval
            if len(dist_interval) == 0:
                self.done = True
            else:
                dist_interval[0] += self.config.dist_start
            return dist_interval
        elif self.config.dist == "poisson":
            dist_interval = list(np.random.poisson(self.config.dist_lam, self.config.dist_size))
            if len(dist_interval) == 0:
                self.done = True
            else:
                dist_interval[0] += self.config.dist_start
            return dist_interval
        else:
            error = f"The distribution '{self.config.dist}' is not supported. ['manual', 'poission']"
            raise Exception(error)

    def generate(self, task_queue: TaskQueue) -> None:
        for task_id, interval in enumerate(self.intervals):
            self.evt_generate = self.env.event()
            yield self.env.timeout(interval)

            task = Task(self.env, task_id, self.config)
            task.ts_arrive = self.env.now
            self.evt_generate.succeed(value=task)
            print(f"{task.name} arrived @ {self.env.now}")

            task_queue.put(task)
