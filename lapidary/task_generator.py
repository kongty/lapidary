import simpy
import numpy as np
from typing import List
from lapidary.task import Task
from lapidary.task_generator_config import TaskGeneratorConfig


class TaskGenerator:
    def __init__(self, env: simpy.Environment, config: TaskGeneratorConfig) -> None:
        self.env = env
        self.task_id = 0
        self.done = False
        self.config = config
        self.arrival_interval = self._generate_arrival_interval()

    def _generate_arrival_interval(self) -> List[int]:
        if self.config.dist == "manual":
            dist = self.config.dist_interval
            if len(dist) == 0:
                self.done = True
            else:
                dist[0] += self.config.dist_start
            return dist
        elif self.config.dist == "poisson":
            dist = list(np.random.poisson(self.config.dist_lam, self.config.dist_size))
            if len(dist) == 0:
                self.done = True
            else:
                dist[0] += self.config.dist_start
            return dist
        else:
            error = f"The distribution '{self.config.dist}' is not supported. ['manual', 'poission']"
            raise Exception(error)

    def arrive(self) -> None:
        if self.config.dist == "manual":
            yield self.env.timeout(self.arrival_interval[self.task_id])
            print(f"{self.config.name} #{self.task_id} arrived @ {self.env.now}")
        elif self.config.dist == "poisson":
            yield self.env.timeout(self.arrival_interval[self.task_id])
            print(f"{self.config.name} #{self.task_id} arrived @ {self.env.now}")

        task = Task(self.task_id)
        task.ts_arrival = self.env.now

        self.task_id += 1

        return task
