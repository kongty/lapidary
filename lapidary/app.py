from typing import List, Tuple
from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    pr_shape: Tuple[int, int]
    pe: int
    mem: int
    input: int
    output: int
    runtime: int


class AppPool:
    def __init__(self, name: str) -> None:
        self.name = name
        self.app_pool = defaultdict(list)

    def add(self, app: str, app_config: AppConfig) -> None:
        self.app_pool[app].append(app_config)

    def get(self, app: str) -> List[AppConfig]:
        return self.app_pool[app]
