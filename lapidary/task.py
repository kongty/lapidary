import simpy
from lapidary.app import AppConfig
from typing import Tuple, List, Generator
from enum import Enum
import logging
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    pending = 1
    running = 2
    done = 3


class Task:
    def __init__(self, env: simpy.Environment, workload_name: str, workload_id: int, task_name: str,
                 app: str, deps: List[str]) -> None:
        self.env = env
        self.name = task_name
        self.workload_name = workload_name
        self.workload_id = workload_id
        self.app = app
        self.tag = f"{self.workload_name}_#{self.workload_id}_{self.name}_{self.app}"
        self.status = TaskStatus.pending
        self.deps = deps

        self.ts_generate: int = 0
        self.ts_schedule: int = 0
        self.ts_done: int = 0

        self.app_config: AppConfig

    def set_app_config(self, app_config: AppConfig) -> None:
        """Set app configuration."""
        self.app_config = app_config

    def proc_execute(self) -> Generator[simpy.events.Event, None, None]:
        """Yield for runtime period."""
        logger.info(f"[@ {self.env.now}] {self.tag} execution starts.")
        yield self.env.timeout(self.app_config.runtime)
        logger.info(f"[@ {self.env.now}] {self.tag} execution finishes.")
        self.ts_done = int(self.env.now)

    def get_pr_shape(self) -> Tuple[int, int]:
        """Return partial region shape."""
        if self.app_config is None:
            raise Exception(f"app configuration is not set for {self.tag}")
        else:
            return self.app_config.pr_shape
