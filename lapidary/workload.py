import os
import yaml
from lapidary.task import Task


class Workload:
    def __init__(self) -> None:
        self.name = 'workload_0'
        self.num_tasks = 0
        self.type = 'once'
        self.tasks = []

    def read_config_file(self, config_file: str) -> None:
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
