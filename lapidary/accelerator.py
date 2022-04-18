from asyncio import Task
from lapidary.app_config import AppConfig
from lapidary.architecture import Architecture
import simpy
from typing import List, Tuple
import numpy as np
from lapidary.partial_region import PartialRegion


class Accelerator:
    def __init__(self, env: simpy.Environment, architecture: Architecture) -> None:
        self.env = env
        self.architecture = architecture
        self.prs = self.generate_pr()
        self.evt_task_done = self.env.event()
        self.task_monitor = 

    def generate_pr(self) -> List[List[PartialRegion]]:

        pr = PartialRegion(height=self.architecture.pr_height,
                           width=self.architecture.pr_width,
                           num_input=self.architecture.pr_num_input,
                           num_output=self.architecture.pr_num_output)
        prs = [[pr] * self.architecture.num_pr_width] * self.architecture.num_pr_height

        return prs

    def execute(self, task: Task, coords: List[Tuple[int, int]]) -> None:
        self.env.process(self._proc_execute(task, coords))

    def _proc_execute(self, task: Task, coords: List[Tuple[int, int]]) -> None:
        yield self.env.process(task.proc_execute())
        self.evt_task_done.succeed()
        self.evt_task_done = self.env.event()

    def allocate(self, task: Task, coords: List[Tuple[int, int]]) -> bool:
        for coord in coords:
            self.prs[coord[1]][coord[0]].is_used = True

    def deallocate(self, task: Task, coords: List[Tuple[int, int]]) -> bool:
        for coord in coords:
            self.prs[coord[1]][coord[0]].is_used = False

    def get_max_rectangle_prs(self) -> List[Tuple[int, int]]:
        """Return left-bottom and right-top coordinates of PRs that creates the maximum size.

        TODO: Expand this to support non-rectangle-like shape.
        """

        return [(0, 0), (7, 0)]

    def get_available_prs(self) -> List[List[bool]]:
        """Return a 2-D mask that indicates which PR is available."""
        pr_avail = [[True] * len(self.prs[0])] * len(self.prs)
        for y in range(len(pr_avail)):
            for x in range(len(pr_avail[0])):
                if self.prs[y][x].is_used:
                    pr_avail[y][x] = False

        return pr_avail
