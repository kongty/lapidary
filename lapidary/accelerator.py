import numpy as np
import yaml
import os
import simpy
from typing import List, Tuple, Optional, Union, Dict
from functools import reduce
from lapidary.app import AppConfig
from lapidary.components import ComponentStatus, NoC, PartialRegion, Bank, OffchipInterface
from lapidary.task import Task


class AcceleratorConfig:
    def __init__(self, config: Optional[Union[str, Dict]] = None) -> None:
        self.name = 'accelerator'
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
            config = os.path.realpath(config)
            if not os.path.exists(config):
                raise Exception("[ERROR] Architecture config file not found")
            else:
                print(f"[LOG] Architecture config file read: {config}")
            with open(config, 'r') as f:
                config = yaml.load(f, Loader=yaml.SafeLoader)

        if 'name' in config:
            self.name = config['name']
        if 'num_glb_banks' in config:
            self.num_glb_banks = config['num_glb_banks']
        if 'num_pr_height' in config:
            self.num_pr_height = config['num_pr_height']
        if 'num_pr_width' in config:
            self.num_pr_width = config['num_pr_width']
        if 'pr_flexible' in config:
            self.pr_flexible = config['pr_flexible']
        if 'pr' in config:
            if 'height' in config['pr']:
                self.pr_height = config['pr']['height']
            if 'width' in config['pr']:
                self.pr_width = config['pr']['width']
            if 'num_input' in config['pr']:
                self.pr_num_input = config['pr']['num_input']
            if 'num_output' in config['pr']:
                self.pr_num_output = config['pr']['num_output']


class Accelerator:
    def __init__(self, env: simpy.Environment, config: Optional[Union[str, Dict]]) -> None:
        self.env = env
        self.config = AcceleratorConfig(config)
        self.offchip_interface = self._generate_offchip_interface()
        self.banks = self._generate_banks()
        self.noc = self._generate_noc()
        self.prs = self._generate_prs()

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
                                          status=ComponentStatus.idle,
                                          task=None,
                                          height=self.config.pr_height,
                                          width=self.config.pr_width,
                                          num_input=self.config.pr_num_input,
                                          num_output=self.config.pr_num_output)

        return prs

    def _generate_banks(self) -> List[Bank]:
        """Return 1d-list of global buffer banks."""
        pass

    def _generate_offchip_interface(self) -> OffchipInterface:
        """Return a DRAM controller."""
        pass

    def _generate_noc(self) -> NoC:
        """Return a NoC."""
        pass

    @property
    def pr_available_mask(self) -> List[List[bool]]:
        """Return a 2-D mask for available prs."""
        if self._pr_available_mask is None:
            pr_mask = [[True] * len(self.prs[0])] * len(self.prs)
            for y in range(len(pr_mask)):
                for x in range(len(pr_mask[0])):
                    if self.prs[y][x].status != ComponentStatus.idle:
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
        self.evt_task_done.succeed(value=task)

    def acknowledge_task_done(self) -> None:
        self.evt_task_done = self.env.event()

    def allocate(self, task: Task, prs: List[PartialRegion]) -> None:
        """Allocate prs to a task."""
        for pr in prs:
            if pr.status != ComponentStatus.idle:
                raise Exception(f"Cannot allocate PR_{pr.id} to {task.tag}. It is not idle.")
            pr.status = ComponentStatus.used
            pr.task = task
        # Initialize pr_mask to None
        self._pr_available_mask = None

    def deallocate(self, prs: List[PartialRegion]) -> None:
        """Deallocate prs."""
        for pr in prs:
            if pr.status == ComponentStatus.idle:
                raise Exception(f"Cannot deallocate PR_{pr.id}. It is already idle.")
            pr.status = ComponentStatus.idle
            pr.task = None
        # Initialize pr_mask to None
        self._pr_available_mask = None

    def map(self, app_config: AppConfig) -> List[PartialRegion]:
        """Return a list of available prs where an app_config can be mapped."""
        prs = self.map_pr(app_config.pr_shape)
        return prs

    def map_pr(self, shape: Tuple[int, int]) -> List[PartialRegion]:
        """Return a list of prs where input shape fits in.

            Parameters
            ----------
            shape: (height, width)
        """
        if self.config.pr_flexible:
            raise NotImplementedError("Flexible PR mapping is not available yet.")
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
