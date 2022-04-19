import os
import yaml
import simpy
from typing import Optional, Union, Dict
from lapidary.task_generator import TaskGenerator
from lapidary.task_queue import TaskQueue


class Workload:
    def __init__(self, env: simpy.Environment, config: Optional[Union[str, Dict]] = None) -> None:
        self.env = env
        self.name = 'workload_0'
        self.task_generators = []
        if config is not None:
            self.set_workload(config)

        self.evt_dispatch = self.env.event()

    def set_workload(self, config: Union[str, Dict]) -> None:
        """Set workload properties with input configuration file."""
        if type(config) is str:
            if not os.path.exists(config):
                raise Exception("[ERROR] Workload config file not found")
            else:
                print(f"[LOG] Workload config file read: {config}")
            with open(config, 'r') as f:
                config = yaml.load(f, Loader=yaml.loader.SafeLoader)

        self.name = config['name']
        for task_config_dict in config["tasks"]:
            self.task_generators.append(TaskGenerator(self.env, task_config_dict))

    def run_dispatch(self, task_queue: TaskQueue):
        """Run task generate proccesses in each task generators."""
        for task_generator in self.task_generators:
            self.env.process(task_generator.proc_generate(task_queue))
