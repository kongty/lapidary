from dataclasses import dataclass
from lapidary.task import Task
from typing import Optional, Tuple


@dataclass
class PartialRegion:
    id: Tuple[int, int]
    is_used: bool
    task: Optional[Task]
    height: int
    width: int
    num_input: int
    num_output: int


@dataclass
class Bank:
    is_used: bool
    task: Optional[Task]
    size: int


@dataclass
class DramController:
    is_used: bool
    bandwidth: int
