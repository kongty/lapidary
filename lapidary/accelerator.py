from asyncio import Task
from lapidary.app_config import AppConfig
from lapidary.architecture import Architecture
import simpy
from typing import List, Tuple
import numpy as np


class Accelerator:
    def __init__(self, env: simpy.Environment, architecture: Architecture) -> None:
        self.env = env
        self.architecture = architecture
        self.pr = np.zeros((self.architecture.num_pr_height, self.architecture.num_pr_width), dtype=int)
        self.evt_task_done = self.env.event()

    def allocate(self, task: Task, pr: np.ndarray):
        pass

    def execute(self, task: Task, app_config: AppConfig, pr: np.ndarray) -> None:
        self.env.process(self._proc_execute(task, app_config, pr))

    def _proc_execute(self, task: Task, app_config: AppConfig, pr: np.ndarray) -> None:
        yield self.env.process(task.proc_execute(app_config.runtime))
        self.evt_task_done.succeed()
        self.evt_task_done = self.env.event()

    # def get_max_rectangle_prs(self) -> List[Tuple[int, int]]:
    #     """Return left-bottom and right-top coordinates of PRs that creates the maximum size of rectangle.

    #     TODO: Expand this to support non-rectangle-like shape.
    #     """

    #     return [(0, 0), (7, 0)]

    def get_available_prs(self) -> np.ndarray:
        """Return a 2-D mask that indicates which PR is available."""
        pr_avail = np.ones((self.architecture.num_pr_height, self.architecture.num_pr_width), dtype=int)
        pr_avail -= self.pr

        return pr_avail
