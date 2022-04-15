from typing import Optional


class TaskConfig:
    def __init__(self, config_dict: Optional[dict]) -> None:
        self.name = 'app_0'
        self.pe = 0
        self.mem = 0
        self.input = 0
        self.output = 0
        self.dist = 'manual'
        self.dist_start = 0
        self.dist_time = []
        self.dist_size = 0
        self.dist_lam = 0
        self.runtime = 0
        if config_dict is not None:
            self.set_task(config_dict)

    def set_task(self, config_dict: dict) -> None:
        self.name = config_dict['name']
        self.pe = config_dict['pe']
        self.mem = config_dict['mem']
        self.input = config_dict['input']
        self.output = config_dict['output']
        self.dist = config_dict['dist']
        self.dist_start = config_dict['dist_start']
        self.runtime = config_dict['runtime']
        if self.dist == 'manual':
            self.dist_interval = config_dict['dist_interval']
        elif self.dist == 'poisson':
            self.dist_lam = config_dict['dist_lam']
            self.dist_size = config_dict['dist_size']
