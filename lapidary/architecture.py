import os
import yaml
from lapidary.architecture_config import ArchitectureConfig


class Architecture:
    def __init__(self) -> None:
        self.config = ArchitectureConfig()

    def read_config_file(self, config_file: str) -> None:
        if not os.path.exists(config_file):
            print("[ERROR] Architecture config file not found")
            exit()
        else:
            print(f"[LOG] Architecture config file read: {config_file}")
        with open(config_file, 'r') as f:
            self.config.set_config(yaml.load(f, Loader=yaml.SafeLoader))
