import os
import yaml
from typing import Optional


class Architecture:
    def __init__(self, config_file: Optional[str] = None) -> None:
        self.name = 'amber'
        self.num_glb_banks = 32
        self.num_pr_height = 1
        self.num_pr_width = 8
        self.pr_flexible = False

        self.pr_height = 16
        self.pr_width = 4
        self.pr_num_input = 4
        self.pr_num_output = 4

        if config_file is not None:
            self.set_architecture(config_file)
        else:
            print(f"[LOG] Use the default architecture config")

    def set_architecture(self, config_file: str) -> None:
        """Set architecture properties with input configuration file."""
        if not os.path.exists(config_file):
            raise Exception("[ERROR] Architecture config file not found")
        else:
            print(f"[LOG] Architecture config file read: {config_file}")
        with open(config_file, 'r') as f:
            config_dict = yaml.load(f, Loader=yaml.SafeLoader)

        self.name = config_dict['name']
        self.num_glb_banks = config_dict['num_glb_banks']
        self.num_pr_height = config_dict['num_pr_height']
        self.num_pr_width = config_dict['num_pr_width']
        self.pr_flexible = config_dict['pr_flexible']
        self.pr_height = config_dict['pr']['height']
        self.pr_width = config_dict['pr']['width']
        self.pr_num_input = config_dict['pr']['num_input']
        self.pr_num_output = config_dict['pr']['num_output']
