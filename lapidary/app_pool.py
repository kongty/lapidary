from lapidary.app_config import AppConfig
from typing import List
from collections import defaultdict


class AppPool:
    def __init__(self, name: str) -> None:
        self.name = name
        self.app_pool = defaultdict(list)

    def add(self, app: str, app_config: AppConfig) -> None:
        self.app_pool[app].append(app_config)

    def get(self, app: str) -> List[AppConfig]:
        return self.app_pool[app]