from dataclasses import dataclass
from lapidary.task import Task
from typing import Optional, Tuple
from enum import Enum


class ComponentStatus(Enum):
    idle = 1
    reserved = 2
    used = 3


@dataclass
class PartialRegion:
    id: Tuple[int, int] = (0, 0)
    status: ComponentStatus = ComponentStatus.idle
    task: Optional[Task] = None
    height: int = 0
    width: int = 0
    num_input: int = 0
    num_output: int = 0


@dataclass
class Bank:
    status: ComponentStatus = ComponentStatus.idle
    task: Optional[Task] = None
    size: int = 0


@dataclass
class OffchipInterface:
    max_bandwidth: int = 0
    bandwidth: int = 0


@dataclass
class NoC:
    max_bandwidth: int = 0
    bandwidth: int = 0
