from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Tuple
if TYPE_CHECKING:
    from lapidary.task import Task
from enum import Enum


class ComponentStatus(Enum):
    idle = 1
    reserved = 2
    used = 3


@dataclass
class PRR:
    id: int = 0
    coord: Tuple[int, int] = (0, 0)
    status: ComponentStatus = ComponentStatus.idle
    task: Optional[Task] = None
    height: int = 0
    width: int = 0
    num_input: int = 0
    num_output: int = 0


@dataclass
class Bank:
    id: int = 0
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
