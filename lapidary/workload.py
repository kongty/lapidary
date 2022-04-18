import os
import yaml
import simpy
from typing import Optional
from lapidary.task_generator import TaskGenerator
from lapidary.task_queue import TaskQueue


class Workload:
    def __init__(self, env: simpy.Environment, config_file: Optional[str] = None) -> None:
        self.env = env
        self.name = 'workload_0'
        self.task_generators = []
        if config_file is not None:
            self.set_workload(config_file)
        self.evt_dispatch = self.env.event()

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
            self.task_generators.append(TaskGenerator(self.env, task_config_dict))

    def run_dispatch(self, task_queue: TaskQueue):
        for task_generator in self.task_generators:
            self.env.process(task_generator.proc_generate(task_queue))
