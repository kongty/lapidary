from __future__ import annotations
import simpy
from dataclasses import dataclass
from typing import TYPE_CHECKING, List
import logging
logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from lapidary.kernel import Kernel


@dataclass
class Timestamp:
    generate: int = 0
    queue: int = 0
    schedule: int = 0
    done: int = 0


class Task:
    def __init__(self, env: simpy.Environment, name: str, id: int) -> None:
        self.env = env
        self.name = name
        self.id = id
        self.tag = f"{self.name}_{self.id}"
        self.timestamp: Timestamp = Timestamp(generate=int(self.env.now))

        # TODO: Change this to graph for fast traversal
        self._kernels: List[Kernel]
        self.next_kernel_idx: int = 0

        # task_done event
        self.evt_task_done = self.env.event()

    @property
    def pending_kernels(self) -> List[Kernel]:
        return self.kernels[self.next_kernel_idx:]

    @property
    def kernels(self) -> List[Kernel]:
        return self._kernels

    @kernels.setter
    def kernels(self, kernels: List[Kernel]) -> None:
        self._kernels = kernels

    # TODO: For now, we just iterate through all pending kernels
    @property
    def ready_kernels(self) -> List[Kernel]:
        ready_kernels = []
        for kernel in self.pending_kernels:
            if len(kernel.deps) == 0:
                ready_kernels.append(kernel)

        return ready_kernels

    def update_dependency(self, kernel: Kernel) -> None:
        for pending_kernel in self.pending_kernels:
            if kernel.name in pending_kernel.deps:
                pending_kernel.deps.remove(kernel.name)
