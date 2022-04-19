import simpy
from lapidary.app import AppConfig
from typing import Tuple


class Task:
    def __init__(self, env: simpy.Environment, task: str, id: int, app: str) -> None:
        self.env = env
        self.task = task
        self.id = id
        self.name = self.task + "_#" + str(self.id)
        self.app = app
        self.ts_arrive = 0
        self.ts_schedule = 0
        self.ts_done = 0
        self.app_config = None

    def set_app_config(self, app_config: AppConfig) -> None:
        """Set app configuration."""
        self.app_config = app_config

    def proc_execute(self) -> None:
        """Yield for runtime period."""
        print(f"[@ {self.env.now}] {self.name} execution starts.")
        yield self.env.timeout(self.app_config.runtime)
        print(f"[@ {self.env.now}] {self.name} execution finishes.")
        self.ts_done = self.env.now

    def get_pr_shape(self) -> Tuple[int, int]:
        """Return partial region shape."""
        if self.app_config is None:
            raise Exception(f"app configuration is not set for {self.name}")
        else:
            return self.app_config.pr_shape
