import numpy as np
import yaml
import os
import simpy
from typing import List, Tuple, Optional, Union, Dict
from functools import reduce
from lapidary.components import PartialRegion, Bank, DramController
from lapidary.task import Task


class AcceleratorConfig:
    def __init__(self, config: Optional[Union[str, Dict]] = None) -> None:
        self.name = 'amber'
        self.num_glb_banks = 32
        self.num_pr_height = 1
        self.num_pr_width = 8
        self.pr_flexible = False

        self.pr_height = 16
        self.pr_width = 4
        self.pr_num_input = 4
        self.pr_num_output = 4

        if config is not None:
            self.set_config(config)

    def set_config(self, config: Union[str, Dict]) -> None:
        """Set architecture properties with input configuration file."""
        if type(config) is str:
            if not os.path.exists(config):
                raise Exception("[ERROR] Architecture config file not found")
            else:
                print(f"[LOG] Architecture config file read: {config}")
            with open(config, 'r') as f:
                config = yaml.load(f, Loader=yaml.SafeLoader)

        self.name = config['name']
        self.num_glb_banks = config['num_glb_banks']
        self.num_pr_height = config['num_pr_height']
        self.num_pr_width = config['num_pr_width']
        self.pr_flexible = config['pr_flexible']
        self.pr_height = config['pr']['height']
        self.pr_width = config['pr']['width']
        self.pr_num_input = config['pr']['num_input']
        self.pr_num_output = config['pr']['num_output']


class Accelerator:
    def __init__(self, env: simpy.Environment, config: Optional[Union[str, Dict]]) -> None:
        self.env = env
        self.config = AcceleratorConfig(config)
        self.prs = self._generate_prs()
        self.banks = self._generate_banks()
        self.dram_controller = self._generate_dram_controller()

        # self.pr_mask is a readonly property
        self._pr_available_mask = [[True] * len(self.prs[0])] * len(self.prs)

        # task_done event
        self.evt_task_done = self.env.event()

    def _generate_prs(self) -> List[List[PartialRegion]]:
        """Return 2d-list of partial regions."""
        prs = [[None] * self.config.num_pr_width] * self.config.num_pr_height
        for y in range(self.config.num_pr_height):
            for x in range(self.config.num_pr_width):
                prs[y][x] = PartialRegion(id=(x, y),
                                          is_used=False,
                                          task=None,
                                          height=self.config.pr_height,
                                          width=self.config.pr_width,
                                          num_input=self.config.pr_num_input,
                                          num_output=self.config.pr_num_output)

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
        self.env.process(self.proc_execute(task, prs))

    def proc_execute(self, task: Task, prs: List[PartialRegion]) -> None:
        """Start task execution process."""
        yield self.env.process(task.proc_execute())
        self.deallocate(prs)
        self.evt_task_done.succeed()
        self.evt_task_done = self.env.event()

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
        if self.config.pr_flexible:
            raise NotImplementedError("Flexible PR allocation is not available yet.")
        else:
            height, width = shape
            # Note: Greedy search algorithm for available prs.
            found = False
            for y in range(self.config.num_pr_height - height + 1):
                for x in range(self.config.num_pr_width - width + 1):
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
