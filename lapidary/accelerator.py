from asyncio import Task
from lapidary.architecture import Architecture
import simpy
from typing import List, Tuple
from functools import reduce
import numpy as np
from lapidary.components import PartialRegion, Bank, DramController


class Accelerator:
    def __init__(self, env: simpy.Environment, architecture: Architecture) -> None:
        self.env = env
        self.architecture = architecture
        self.prs = self._generate_prs()
        self.banks = self._generate_banks()
        self.dram_controller = self._generate_dram_controller()

        # self.pr_mask is a readonly property
        self._pr_available_mask = [[True] * len(self.prs[0])] * len(self.prs)

        # task_done event
        self.evt_task_done = self.env.event()

    def _generate_prs(self) -> List[List[PartialRegion]]:
        """Return 2d-list of partial regions."""
        prs = [[None] * self.architecture.num_pr_width] * self.architecture.num_pr_height
        for y in range(self.architecture.num_pr_height):
            for x in range(self.architecture.num_pr_width):
                prs[y][x] = PartialRegion(id=(x, y),
                                          is_used=False,
                                          task=None,
                                          height=self.architecture.pr_height,
                                          width=self.architecture.pr_width,
                                          num_input=self.architecture.pr_num_input,
                                          num_output=self.architecture.pr_num_output)

        return prs

    def _generate_banks(self) -> List[Bank]:
        """Return 1d-list of global buffer banks."""
        pass

    def _generate_dram_controller(self) -> DramController:
        """Return a DRAM controller."""
        pass

    @property
    def pr_available_mask(self) -> List[List[bool]]:
        """Return a 2-D mask for available prs."""
        if self._pr_available_mask is None:
            pr_mask = [[True] * len(self.prs[0])] * len(self.prs)
            for y in range(len(pr_mask)):
                for x in range(len(pr_mask[0])):
                    if self.prs[y][x].is_used:
                        pr_mask[y][x] = False
            self._pr_available_mask = pr_mask

        return self._pr_available_mask

    def execute(self, task: Task, prs: List[PartialRegion]) -> None:
        """Start task execution process."""
        self.allocate(task, prs)
        yield self.env.process(task.proc_execute())
        self.evt_task_done.succeed()
        self.evt_task_done = self.env.event()
        self.deallocate(prs)

    def allocate(self, task: Task, prs: List[PartialRegion]) -> bool:
        """Allocate prs to a task."""
        prs_is_used = [pr.is_used for pr in prs]
        if reduce(lambda x, y: x or y, prs_is_used) is True:
            return False
        else:
            for pr in prs:
                pr.is_used = True
                pr.task = task
            # Initialize pr_mask to None
            self._pr_available_mask = None
            return True

    def deallocate(self, prs: List[PartialRegion]) -> bool:
        """Deallocate prs."""
        prs_is_used = [pr.is_used for pr in prs]
        if reduce(lambda x, y: x and y, prs_is_used) is False:
            return False
        else:
            for pr in prs:
                pr.is_used = False
                pr.task = None
            # Initialize pr_mask to None
            self._pr_available_mask = None
            return True

    def map(self, task: Task) -> List[PartialRegion]:
        """Return a list of available prs where a task can be mapped."""
        pr_shape = task.get_pr_shape()
        prs = self.get_available_prs(pr_shape)
        return prs

    def get_available_prs(self, shape: Tuple[int, int]) -> List[PartialRegion]:
        """Return a list of available prs where input shape fits in.

            Parameters
            ----------
            shape: (height, width)
        """
        if self.architecture.pr_flexible:
            raise NotImplementedError("Flexible PR allocation is not available yet.")
        else:
            height, width = shape
            # Note: Greedy search algorithm for available prs.
            found = False
            for y in range(self.architecture.num_pr_height - height + 1):
                for x in range(self.architecture.num_pr_width - width + 1):
                    pr_mask = np.array(self.pr_available_mask)[y:y+height, x:x+width]
                    is_available = reduce(lambda x, y: x and y, pr_mask.flatten())
                    if is_available:
                        found = True
                        break

            if found is False:
                return []
            else:
                prs = list(np.array(self.prs)[y:y+height, x:x+width].flatten())
                return prs
