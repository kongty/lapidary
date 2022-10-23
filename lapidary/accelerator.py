from __future__ import annotations
import numpy as np
import math
import yaml
import os
import simpy
from typing import TYPE_CHECKING, List, Tuple, Optional, Union, TypedDict, Generator
from functools import reduce
from lapidary.app import LayerConfig
from lapidary.components import ComponentStatus, NoC, Core, Bank, OffchipInterface
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
        self.cores = self._generate_cores()

        # self.prr_mask is a readonly property
        self._core_available_mask: Optional[List[List[bool]]] = [
            [True for _ in range(len(self.cores[0]))] for _ in range(len(self.cores))]
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

    def _generate_cores(self) -> List[List[Core]]:
        """Return 2d-list of cores."""
        prrs: List[List[Core]] = [[Core() for _ in range(self.config.num_prr_width)]
                                  for _ in range(self.config.num_prr_height)]
        for y in range(self.config.num_prr_height):
            for x in range(self.config.num_prr_width):
                prrs[y][x] = Core(id=(y*self.config.num_prr_width + x),
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
    def core_available_mask(self) -> List[List[bool]]:
        """Return a 2-D mask for available cores."""
        if self._core_available_mask is None:
            core_mask = [[True for _ in range(len(self.cores[0]))] for _ in range(len(self.cores))]
            for y in range(len(core_mask)):
                for x in range(len(core_mask[0])):
                    if self.cores[y][x].status != ComponentStatus.idle:
                        core_mask[y][x] = False
            self._core_available_mask = core_mask

        return self._core_available_mask

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
        self.deallocate(kernel.cores, kernel.banks)
        self.evt_kernel_done.succeed(value=(kernel, mut_kernel_done))

    def acknowledge_kernel_done(self, mut_kernel_done: simpy.resources.resource.Request) -> None:
        self.scheduler.mut_controller.release(mut_kernel_done)
        self.evt_kernel_done = self.env.event()

    def allocate(self, kernel: Kernel, cores: List[Core], banks: List[Bank]) -> None:
        """Allocate cores to a task."""
        kernel.set_cores(cores)
        kernel.set_banks(banks)
        for core in cores:
            if core.status != ComponentStatus.idle:
                raise Exception(f"Cannot allocate Core_{core.id} to {kernel.tag}. It is not idle.")
            core.status = ComponentStatus.used
            core.kernel = kernel
        for bank in banks:
            if bank.status != ComponentStatus.idle:
                raise Exception(f"Cannot allocate BANK_{bank.id} to {kernel.tag}. It is not idle.")
            bank.status = ComponentStatus.used
            bank.kernel = kernel
        # Initialize core_mask to None
        self._core_available_mask = None
        self._bank_available_mask = None

    def deallocate(self, cores: List[Core], banks: List[Bank]) -> None:
        """Deallocate cores."""
        for core in cores:
            if core.status == ComponentStatus.idle:
                raise Exception(f"Cannot deallocate PRR_{core.id}. It is already idle.")
            core.status = ComponentStatus.idle
            core.kernel = None
        for bank in banks:
            if bank.status == ComponentStatus.idle:
                raise Exception(f"Cannot deallocate Bank_{bank.id}. It is already idle.")
            bank.status = ComponentStatus.idle
            bank.kernel = None
        # Initialize core_mask to None
        self._core_available_mask = None
        self._bank_available_mask = None

    def map(self, layer_config: LayerConfig) -> Tuple[List[Core], List[Bank]]:
        """Return a list of available prrs where an app_config can be mapped."""
        cores, banks = self.map_core(layer_config.core_shape, layer_config.input + layer_config.output)
        return cores, banks

    def map_core(self, shape: Tuple[int, int], num_io: int) -> Tuple[List[Core], List[Bank]]:
        """Return a list of prs where input shape fits in.

            Parameters
            ----------
            shape: (height, width)
            num_io: number of inputs and outputs
        """
        if self.config.partition == PartitionType.FLEXIBLE:
            height, width = shape
            total_required_core = height * width
            total_required_banks = num_io
            # Note: Greedy search algorithm for available prrs.
            found_core = False
            found_bank = False
            cores = []
            banks = []
            found_cores = 0
            num_found_banks = 0
            core_available_mask = self.core_available_mask
            bank_available_mask = self.bank_available_mask
            for y in range(self.config.num_prr_height):
                for x in range(self.config.num_prr_width):
                    if core_available_mask[y][x]:
                        cores.append(self.cores[y][x])
                        found_cores += 1
                    if found_cores >= total_required_core:
                        found_core = True
                        break
                if found_core is True:
                    break

            for x in range(self.config.num_glb_banks):
                if bank_available_mask[x]:
                    banks.append(self.banks[x])
                    num_found_banks += 1
                if num_found_banks >= total_required_banks:
                    found_bank = True
                    break

            if found_core is False or found_bank is False:
                return [], []
            else:
                return cores, banks
        elif self.config.partition == PartitionType.FLEXIBLE:
            height, width = shape
            total_required_core = height * width
            total_required_banks = num_io
            # Note: Greedy search algorithm for available cores.
            found_core = False
            cores = []
            core_available_mask = self.core_available_mask

            for y in range(self.config.num_prr_height - height + 1):
                for x in range(self.config.num_prr_width - width + 1):
                    prr_mask = np.array(core_available_mask)[y:y+height, x:x+width]
                    is_available = reduce(lambda x, y: x and y, prr_mask.flatten())
                    if is_available:
                        found_core = True
                        break
                if found_core is True:
                    cores = list(np.array(self.cores)[y:y+height, x:x+width].flatten())
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

            if found_core is False or found_bank is False:
                return [], []
            else:
                return cores, banks
        elif self.config.partition == PartitionType.VARIABLE:
            height, width = shape
            banks_per_prr = self.config.num_glb_banks // self.config.num_prr_width
            # TODO: Assume PRR is also 1-D for WDDSA paper
            if num_io > width * banks_per_prr:
                width = int(math.ceil(num_io / banks_per_prr))
            # Note: Greedy search algorithm for available prrs.
            found_core = False
            core_available_mask = self.core_available_mask
            for y in range(self.config.num_prr_height - height + 1):
                for x in range(self.config.num_prr_width - width + 1):
                    prr_mask = np.array(core_available_mask)[y:y+height, x:x+width]
                    is_available = reduce(lambda x, y: x and y, prr_mask.flatten())
                    if is_available:
                        found_core = True
                        break
                if found_core is True:
                    break

            if found_core is False:
                return [], []
            else:
                cores = list(np.array(self.cores)[y:y+height, x:x+width].flatten())
                banks = self.banks[x:x+width]
                return cores, banks
        else:
            raise Exception(f"Partition type should be either 'fixed', 'variable', or 'flexible'")
