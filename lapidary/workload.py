import simpy
import os
import yaml
import logging
from typing import Dict, Optional, Union, List
from lapidary.application import Application, ApplicationConfigType
from lapidary.task_queue import TaskQueue
logger = logging.getLogger(__name__)


class Workload:
    def __init__(self, env: simpy.Environment,  config: Optional[Union[str, Dict[str, ApplicationConfigType]]] = None):
        self.env = env
        self.applications: List[Application] = []
        if config is not None:
            self.set_workload(config)

    def set_workload(self, config: Union[str, Dict[str, ApplicationConfigType]]) -> None:
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

        for app_k, app_v in config_dict:
            self.applications.append(Application(self.env, app_k, app_v))

    def run_dispatch(self, task_queue: TaskQueue) -> None:
        """Run dispatch proccess of the application."""
        self.env.process(self.dispatch(task_queue))
