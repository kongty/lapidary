from lapidary.config import Config
import os


class Lapidary:
    def __init__(self, config=''):
        if not os.path.exists(config):
            print("[ERROR] Config file not found")
            exit()
        else:
            self.config_file = config
            self.config = Config()
            print(f"[LOG] Config file read: {self.config_file}")
            self.config.read_config_file(self.config_file)

    def run(self):
        self.config.print_config()
