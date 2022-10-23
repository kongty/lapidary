from typing import Dict, List
from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class LayerConfig:
    num_cores: int = 0
    glb_size: int = 0
    runtime: int = 0
    avg_offchip_bw: int = 0
    avg_noc_bw: int = 0


class DNNPool:
    def __init__(self, name: str) -> None:
        self.name = name
        self.app_pool: Dict[str, List[LayerConfig]] = defaultdict(list)

    def add(self, app: str, app_config: LayerConfig) -> None:
        self.app_pool[app].append(app_config)

    def get(self, app: str) -> List[LayerConfig]:
        return self.app_pool[app]
