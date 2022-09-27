import simpy
import os
import yaml
from typing import Dict, Optional, Union, List
from lapidary.scheduler import Scheduler
from lapidary.task_generator import TaskGenerator, TaskGeneratorConfigType
from lapidary.util.task_logger import TaskLogger
import logging
logger = logging.getLogger(__name__)


class Workload:
    def __init__(self, env: simpy.Environment,  config: Optional[Union[str, Dict[str, TaskGeneratorConfigType]]] = None,
                 task_logger: TaskLogger = None):
        self.env = env
        self.task_logger = task_logger
        self.task_generators: List[TaskGenerator] = []
        if config is not None:
            self.set_workload(config)

    def set_workload(self, config: Union[str, Dict[str, TaskGeneratorConfigType]]) -> None:
        """Set workload properties with input configuration file."""
        if isinstance(config, str):
            config = os.path.realpath(config)
            if not os.path.exists(config):
                raise Exception("[ERROR] Workload config file not found")
            else:
                logger.info(f"Workload config file read: {config}")

            with open(config, 'r') as f:
                config_dict = yaml.load(f, Loader=yaml.loader.SafeLoader)
        else:
            config_dict = config

        for name, config in config_dict.items():
            self.task_generators.append(TaskGenerator(self.env, name, config, self.task_logger))

    def run_generate(self) -> None:
        """Run generate proccess of the task_generators."""
        for task_generator in self.task_generators:
            self.env.process(task_generator.generate())

    def set_scheduler(self, scheduler: Scheduler) -> None:
        """Set a scheduler for each task_generator."""
        for task_generator in self.task_generators:
            task_generator.set_scheduler(scheduler)
