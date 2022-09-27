from __future__ import annotations
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


class Task:
    def __init__(self, name: str, id: int, kernels: List[Kernel], ts_generate: int) -> None:
        self.name = name
        self.id = id
        self.tag = f"{self.name}_{self.id}"
        self.timestamp: Timestamp = Timestamp(generate=ts_generate)

        # TODO: We assume Task is composed of kernels with sequential dependency (e.g. DNN layers)
        self.kernels: List[Kernel]
        self.next_kernel_idx: int = 0

        # task_done event
        self.evt_task_done = self.env.event()

    def set_kernels(self, kernels: List[Kernel]):
        self.kernels = kernels

    def get_pending_kernels(self) -> List[Kernel]:
        return self.kernels[self.next_kernel_idx:]

    def get_ready_kernels(self) -> List[Kernel]:
        return self.kernels[self.next_kernel_idx]

    def update_dependency(self, kernel: Kernel) -> None:
        for pending_kernel in self.get_pending_kernels:
            if kernel.name in pending_kernel.deps:
                pending_kernel.deps.remove(kernel)
