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
    id: Tuple[int, int]
    status: ComponentStatus
    task: Optional[Task]
    height: int
    width: int
    num_input: int
    num_output: int


@dataclass
class Bank:
    status: ComponentStatus
    task: Optional[Task]
    size: int


@dataclass
class OffchipInterface:
    bandwidth: int


@dataclass
class NoC:
    bandwidth: int
