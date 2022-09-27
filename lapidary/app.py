from typing import Dict, List, Tuple
from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    prr_shape: Tuple[int, int] = (0, 0)
    pe: int = 0
    mem: int = 0
    input: int = 0
    output: int = 0
    glb_size: int = 0
    offchip_bw: int = 0
    runtime: int = 0


class AppPool:
    def __init__(self, name: str) -> None:
        self.name = name
        self.app_pool: Dict[str, List[AppConfig]] = defaultdict(list)

    def add(self, app: str, app_config: AppConfig) -> None:
        self.app_pool[app].append(app_config)

    def get(self, app: str) -> List[AppConfig]:
        return self.app_pool[app]
