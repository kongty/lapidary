import os
import yaml
import simpy
from typing import Optional
from lapidary.task_config import TaskConfig
from lapidary.task import Task


class Workload:
    def __init__(self, env: simpy.Environment, config_file: Optional[str] = None) -> None:
        self.env = env
        self.name = 'workload_0'
        self.tasks = []
        if config_file is not None:
            self.set_workload(config_file)

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
            task_config = TaskConfig(task_config_dict)
            self.tasks.append(Task(self.env, task_config))

    def dispatch(self):
        # TODO:
        # Use | expression of task arrive proccess
        pass
