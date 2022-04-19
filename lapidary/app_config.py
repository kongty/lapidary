from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class AppConfig:
    pr_shape: Tuple[int, int]
    pe: int
    mem: int
    input: int
    output: int
    runtime: int
