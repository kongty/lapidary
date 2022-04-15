import os
import yaml
import simpy
from typing import Optional
from lapidary.task_generator_config import TaskGeneratorConfig
from lapidary.task_generator import TaskGenerator


class Workload:
    def __init__(self, env: simpy.Environment, config_file: Optional[str] = None) -> None:
        self.env = env
        self.name = 'workload_0'
        self.task_generators = []
        if config_file is not None:
            self.set_workload(config_file)

        self.dispatch_proc = self.env.process(self.dispatch())

    def set_workload(self, config_file: str) -> None:
        if not os.path.exists(config_file):
            print("[ERROR] Workload config file not found")
            exit()
        else:
            print(f"[LOG] Workload config file read: {config_file}")
        with open(config_file, 'r') as f:
            config = yaml.load(f, Loader=yaml.loader.SafeLoader)

        self.name = config['name']
        for task_config_dict in config["tasks"]:
            task_config = TaskGeneratorConfig(task_config_dict)
            self.task_generators.append(TaskGenerator(self.env, task_config))

    def dispatch(self):
        for task_gen in self.task_generators:
            if 