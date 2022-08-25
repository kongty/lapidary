from __future__ import annotations
import simpy
from vault.app import AppConfig
from typing import TYPE_CHECKING, Tuple, List
if TYPE_CHECKING:
    from vault.components import PRR
from enum import Enum
import logging
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = 1
    RUNNING = 2
    DONE = 3


class Task:
    def __init__(self, env: simpy.Environment, query_name: str, query_id: int, task_name: str,
                 app: str, deps: List[str]) -> None:
        self.env = env
        self.name = task_name
        self.query_name = query_name
        self.query_id = query_id
        self.app = app
        self.tag = f"{self.query_name}_#{self.query_id}_{self.name}"
        self.status = TaskStatus.PENDING
        self.deps = deps

        self.ts_dispatch: int = 0
        self.ts_queue: int = 0
        self.ts_schedule: int = 0
        self.ts_done: int = 0
        self.prrs: List[PRR] = []
        self.banks: List[Bank] = []

        self.app_config: AppConfig

    def set_app_config(self, app_config: AppConfig) -> None:
        """Set app configuration."""
        self.app_config = app_config

    def get_pr_shape(self) -> Tuple[int, int]:
        """Return partial region shape."""
        if self.app_config is None:
            raise Exception(f"app configuration is not set for {self.tag}")
        else:
            return self.app_config.prr_shape

    def update_deps(self, deps: List[str]):
        self.deps = deps

    def set_prrs(self, prrs: List[PRR]) -> None:
        self.prrs = prrs

    def set_banks(self, banks: List[Bank]) -> None:
        self.banks = banks
