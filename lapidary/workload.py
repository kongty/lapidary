import os
import yaml
from typing import Optional
from lapidary.task import Task


class Workload:
    def __init__(self, config_file: Optional[str] = None) -> None:
        self.name = 'workload_0'
        self.num_tasks = 0
        self.type = 'once'
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
        self.type = config['type']
        self.num_tasks = len(config['tasks'])

        for task_config in config["tasks"]:
            task = Task(task_config)
            self.tasks.append(task)
