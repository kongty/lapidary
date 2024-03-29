from __future__ import annotations
from dataclasses import dataclass
from lapidary.app import AppConfig
from typing import TYPE_CHECKING, Tuple, List
if TYPE_CHECKING:
    from lapidary.components import PRR, Bank
    from lapidary.task import Task
from enum import Enum
import logging
logger = logging.getLogger(__name__)


@dataclass
class Timestamp:
    schedule: int = 0
    done: int = 0


class KernelStatus(Enum):
    PENDING = 1
    RUNNING = 2
    DONE = 3


class Kernel:
    def __init__(self, task: Task, name: str, app: str, deps: List[str]) -> None:
        self.task = task
        self.name = name
        self.tag = f"{self.task.tag}_{self.name}"
        self.app = app
        self.status = KernelStatus.PENDING
        self.deps = deps

        self.timestamp = Timestamp()

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
