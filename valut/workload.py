import simpy
import os
import yaml
from typing import Dict, Optional, Union, List
from lapidary.query import Query, QueryConfigType
from lapidary.task_queue import TaskQueue
from util.logger import Logger
import logging
logger = logging.getLogger(__name__)


class Workload:
    def __init__(self, env: simpy.Environment,  config: Optional[Union[str, Dict[str, QueryConfigType]]] = None):
        self.env = env
        self.queries: List[Query] = []
        if config is not None:
            self.set_workload(config)

    def set_workload(self, config: Union[str, Dict[str, QueryConfigType]]) -> None:
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

        for app_k, app_v in config_dict.items():
            self.queries.append(Query(self.env, app_k, app_v))

    def run_dispatch(self, task_logger: Logger) -> None:
        """Run dispatch proccess of the queries."""
        for query in self.queries:
            self.env.process(query.dispatch(task_logger))

    def set_task_queue(self, task_queue: TaskQueue) -> None:
        """Set a task_queue for each query."""
        for query in self.queries:
            query.set_task_queue(task_queue)
