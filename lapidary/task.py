from typing import Optional


class Task:
    def __init__(self, config_dict: Optional[dict]) -> None:
        self.name = 'task_0'
        self.pe = 0
        self.mem = 0
        self.input = 0
        self.output = 0
        if config_dict is not None:
            self.set_task(config_dict)

    def set_task(self, config_dict: dict) -> None:
        self.name = config_dict['name']
        self.pe = config_dict['pe']
        self.mem = config_dict['mem']
        self.input = config_dict['input']
        self.output = config_dict['output']
