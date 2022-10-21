from __future__ import annotations
import numpy as np
import math
import yaml
import os
import simpy
from typing import TYPE_CHECKING, List, Tuple, Optional, Union, TypedDict, Generator
from functools import reduce
from lapidary.app import LayerConfig
from lapidary.components import ComponentStatus, NoC, PRR, Bank, OffchipInterface
from lapidary.kernel import Kernel
if TYPE_CHECKING:
    from lapidary.scheduler import Scheduler
from enum import Enum
import logging
logger = logging.getLogger(__name__)


class PartitionType(Enum):
    FIXED = 1
    VARIABLE = 2
    FLEXIBLE = 3
    FULL_FLEXIBLE = 4


class AcceleratorConfigType(TypedDict):
    name: str
    num_glb_banks: int
    num_cores: int
    num_pes_per_core: int
    noc_bw: int
    offchip_bw: int


class AcceleratorConfig:
    def __init__(self, config: Optional[Union[str, AcceleratorConfigType]] = None) -> None:
        self.name = 'accelerator'
        self.num_glb_banks = 32
        self.num_cores = 8
        self.num_pes_per_core = 64
        self.partition = PartitionType.FIXED

        if config is not None:
            self.set_config(config)

    def set_config(self, config: Union[str, AcceleratorConfigType]) -> None:
        """Set architecture properties with input configuration file."""
        if isinstance(config, str):
            config = os.path.realpath(config)
            if not os.path.exists(config):
                raise Exception("[ERROR] Architecture config file not found")
            else:
                logger.info(f"Architecture config file read: {config}")
            with open(config, 'r') as f:
                config_dict = yaml.load(f, Loader=yaml.SafeLoader)
        else:
            config_dict = config

        self.name = config_dict['name']
        self.num_glb_banks = config_dict['num_glb_banks']
        self.num_cores = config_dict['num_cores']
        self.num_pes_per_core = config_dict['num_pes_per_core']
        if config_dict['partition'].lower() == 'fixed':
            self.partition = PartitionType.FIXED
        elif config_dict['partition'].lower() == 'variable':
            self.partition = PartitionType.VARIABLE
        elif config_dict['partition'].lower() == 'flexible':
            self.partition = PartitionType.FLEXIBLE
        else:
            raise Exception(f"Partition type should be either 'fixed', 'variable', or 'flexible'")


class Accelerator:
    def __init__(self, config: Optional[Union[str, AcceleratorConfigType]]) -> None:
        self.config = AcceleratorConfig(config)
        # self.execution_delay = 10
        self.offchip_interface = self._generate_offchip_interface()
        self.banks = self._generate_banks()
        self.noc = self._generate_noc()
        self.prrs = self._generate_prrs()

        # self.prr_mask is a readonly property
        self._prr_available_mask: Optional[List[List[bool]]] = [
            [True for _ in range(len(self.prrs[0]))] for _ in range(len(self.prrs))]
        self._bank_available_mask: Optional[List[bool]] = [True for _ in range(len(self.banks))]

        self.scheduler: Scheduler

    def set_simulator(self, env: simpy.Environment) -> None:
        self.env = env

        # task_done event
        self.evt_kernel_done = self.env.event()
        self.interrupt_controller = simpy.Resource(self.env, capacity=1)

    def set_scheduler(self, scheduler: Scheduler) -> None:
        """Set a scheduler for accelerator."""
        self.scheduler = scheduler

    def _generate_prrs(self) -> List[List[PRR]]:
        """Return 2d-list of partial regions."""
        prrs: List[List[PRR]] = [[PRR() for _ in range(self.config.num_prr_width)]
                                 for _ in range(self.config.num_prr_height)]
        for y in range(self.config.num_prr_height):
            for x in range(self.config.num_prr_width):
                prrs[y][x] = PRR(id=(y*self.config.num_prr_width + x),
                                 coord=(x, y),
                                 status=ComponentStatus.idle,
                                 kernel=None,
                                 height=self.config.prr_height,
                                 width=self.config.prr_width,
                                 num_input=self.config.prr_num_input,
                                 num_output=self.config.prr_num_output)

        return prrs

    def _generate_banks(self) -> List[Bank]:
        """Return 1d-list of global buffer banks."""
        # TODO: Set bank size to 0 for now.
        banks: List[Bank] = [Bank(id=i, status=ComponentStatus.idle, kernel=None, size=0)
                             for i in range(self.config.num_glb_banks)]
        return banks

    def _generate_offchip_interface(self) -> OffchipInterface:
        """Return an offchip interface."""
        offchip_interface = OffchipInterface()
        return offchip_interface

    def _generate_noc(self) -> NoC:
        """Return a NoC."""
        noc = NoC()
        return noc

    @property
    def prr_available_mask(self) -> List[List[bool]]:
        """Return a 2-D mask for available prrs."""
        if self._prr_available_mask is None:
            prr_mask = [[True for _ in range(len(self.prrs[0]))] for _ in range(len(self.prrs))]
            for y in range(len(prr_mask)):
                for x in range(len(prr_mask[0])):
                    if self.prrs[y][x].status != ComponentStatus.idle:
                        prr_mask[y][x] = False
            self._prr_available_mask = prr_mask

        return self._prr_available_mask

    @property
    def bank_available_mask(self) -> List[bool]:
        """Return a 1-D mask for available banks."""
        if self._bank_available_mask is None:
            bank_mask = [True for _ in range(len(self.banks))]
            for x in range(len(bank_mask)):
                if self.banks[x].status != ComponentStatus.idle:
                    bank_mask[x] = False
            self._bank_available_mask = bank_mask

        return self._bank_available_mask

    def execute(self, kernel: Kernel) -> None:
        """Start kernel execution process."""
        logger.debug(f"[@ {self.env.now}] {kernel.tag} execution starts.")
        self.env.process(self.proc_execute(kernel))

    def proc_execute(self, kernel: Kernel) -> Generator[simpy.events.Event, None, None]:
        """Start kernel execution process."""
        yield self.env.timeout(kernel.app_config.runtime)
        kernel.timestamp.done = int(self.env.now)
        logger.debug(f"[@ {self.env.now}] {kernel.tag} execution finishes.")

        # Controller is a shared resource
        mut_kernel_done = self.scheduler.mut_controller.request()
        yield mut_kernel_done
        self.deallocate(kernel.prrs, kernel.banks)
        self.evt_kernel_done.succeed(value=(kernel, mut_kernel_done))

    def acknowledge_kernel_done(self, mut_kernel_done: simpy.resources.resource.Request) -> None:
        self.scheduler.mut_controller.release(mut_kernel_done)
        self.evt_kernel_done = self.env.event()

    def allocate(self, kernel: Kernel, prrs: List[PRR], banks: List[Bank]) -> None:
        """Allocate prrs to a task."""
        kernel.set_prrs(prrs)
        kernel.set_banks(banks)
        for prr in prrs:
            if prr.status != ComponentStatus.idle:
                raise Exception(f"Cannot allocate PRR_{prr.id} to {kernel.tag}. It is not idle.")
            prr.status = ComponentStatus.used
            prr.kernel = kernel
        for bank in banks:
            if bank.status != ComponentStatus.idle:
                raise Exception(f"Cannot allocate BANK_{bank.id} to {kernel.tag}. It is not idle.")
            bank.status = ComponentStatus.used
            bank.kernel = kernel
        # Initialize prr_mask to None
        self._prr_available_mask = None
        self._bank_available_mask = None

    def deallocate(self, prrs: List[PRR], banks: List[Bank]) -> None:
        """Deallocate prrs."""
        for prr in prrs:
            if prr.status == ComponentStatus.idle:
                raise Exception(f"Cannot deallocate PRR_{prr.id}. It is already idle.")
            prr.status = ComponentStatus.idle
            prr.kernel = None
        for bank in banks:
            if bank.status == ComponentStatus.idle:
                raise Exception(f"Cannot deallocate Bank_{bank.id}. It is already idle.")
            bank.status = ComponentStatus.idle
            bank.kernel = None
        # Initialize prr_mask to None
        self._prr_available_mask = None
        self._bank_available_mask = None

    def map(self, app_config: LayerConfig) -> Tuple[List[PRR], List[Bank]]:
        """Return a list of available prrs where an app_config can be mapped."""
        prrs, banks = self.map_prr(app_config.prr_shape, app_config.input + app_config.output)
        return prrs, banks

    def map_prr(self, shape: Tuple[int, int], num_io: int) -> Tuple[List[PRR], List[Bank]]:
        """Return a list of prs where input shape fits in.

            Parameters
            ----------
            shape: (height, width)
            num_io: number of inputs and outputs
        """
        if self.config.partition == PartitionType.FULL_FLEXIBLE:
            height, width = shape
            total_required_prr = height * width
            total_required_banks = num_io
            # Note: Greedy search algorithm for available prrs.
            found_prr = False
            found_bank = False
            prrs = []
            banks = []
            found_prrs = 0
            num_found_banks = 0
            prr_available_mask = self.prr_available_mask
            bank_available_mask = self.bank_available_mask
            for y in range(self.config.num_prr_height):
                for x in range(self.config.num_prr_width):
                    if prr_available_mask[y][x]:
                        prrs.append(self.prrs[y][x])
                        found_prrs += 1
                    if found_prrs >= total_required_prr:
                        found_prr = True
                        break
                if found_prr is True:
                    break

            for x in range(self.config.num_glb_banks):
                if bank_available_mask[x]:
                    banks.append(self.banks[x])
                    num_found_banks += 1
                if num_found_banks >= total_required_banks:
                    found_bank = True
                    break

            if found_prr is False or found_bank is False:
                return [], []
            else:
                return prrs, banks
        elif self.config.partition == PartitionType.FLEXIBLE:
            height, width = shape
            total_required_prr = height * width
            total_required_banks = num_io
            # Note: Greedy search algorithm for available prrs.
            found_prr = False
            prrs = []
            prr_available_mask = self.prr_available_mask

            for y in range(self.config.num_prr_height - height + 1):
                for x in range(self.config.num_prr_width - width + 1):
                    prr_mask = np.array(prr_available_mask)[y:y+height, x:x+width]
                    is_available = reduce(lambda x, y: x and y, prr_mask.flatten())
                    if is_available:
                        found_prr = True
                        break
                if found_prr is True:
                    prrs = list(np.array(self.prrs)[y:y+height, x:x+width].flatten())
                    break

            found_bank = False
            banks = []
            num_found_banks = 0
            bank_available_mask = self.bank_available_mask
            for x in range(self.config.num_glb_banks):
                if bank_available_mask[x]:
                    banks.append(self.banks[x])
                    num_found_banks += 1
                if num_found_banks >= total_required_banks:
                    found_bank = True
                    break

            if found_prr is False or found_bank is False:
                return [], []
            else:
                return prrs, banks
        elif self.config.partition == PartitionType.VARIABLE:
            height, width = shape
            banks_per_prr = self.config.num_glb_banks // self.config.num_prr_width
            # TODO: Assume PRR is also 1-D for WDDSA paper
            if num_io > width * banks_per_prr:
                width = int(math.ceil(num_io / banks_per_prr))
            # Note: Greedy search algorithm for available prrs.
            found_prr = False
            prr_available_mask = self.prr_available_mask
            for y in range(self.config.num_prr_height - height + 1):
                for x in range(self.config.num_prr_width - width + 1):
                    prr_mask = np.array(prr_available_mask)[y:y+height, x:x+width]
                    is_available = reduce(lambda x, y: x and y, prr_mask.flatten())
                    if is_available:
                        found_prr = True
                        break
                if found_prr is True:
                    break

            if found_prr is False:
                return [], []
            else:
                prrs = list(np.array(self.prrs)[y:y+height, x:x+width].flatten())
                banks = self.banks[x:x+width]
                return prrs, banks
        else:
            raise Exception(f"Partition type should be either 'fixed', 'variable', or 'flexible'")
