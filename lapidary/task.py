from __future__ import annotations  # Required for self references in type checking
import simpy
from lapidary.app import AppConfig
from typing import Tuple, List
from enum import Enum


class TaskStatus(Enum):
    pending = 1
    running = 2
    done = 3


class Task:
    def __init__(self, env: simpy.Environment, workload_name: str, workload_id: int, task_name: str,
                 app: str, deps: List['Task']) -> None:
        self.env = env
        self.name = task_name
        self.workload_name = workload_name
        self.workload_id = workload_id
        self.app = app
        self.tag = self.workload_name + "_#" + str(self.workload_id) + "_" + self.name + "_" + self.app
        self.status = TaskStatus.pending
        self.deps = deps

        self.ts_arrive = 0
        self.ts_schedule = 0
        self.ts_done = 0

        self.app_config = None

    def set_app_config(self, app_config: AppConfig) -> None:
        """Set app configuration."""
        self.app_config = app_config

    def proc_execute(self) -> None:
        """Yield for runtime period."""
        print(f"[@ {self.env.now}] {self.tag} execution starts.")
        yield self.env.timeout(self.app_config.runtime)
        print(f"[@ {self.env.now}] {self.tag} execution finishes.")
        self.ts_done = self.env.now

    def get_pr_shape(self) -> Tuple[int, int]:
        """Return partial region shape."""
        if self.app_config is None:
            raise Exception(f"app configuration is not set for {self.tag}")
        else:
            return self.app_config.pr_shape
