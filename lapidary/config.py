import yaml


class Config:
    def __init__(self):
        self.name = 'amber'

        self.num_glb_banks = 32
        self.num_pr = 8
        self.pr_height = 16
        self.pr_width = 4
        self.pr_num_input = 4
        self.pr_num_output = 4

    def read_config_file(self, config_file):
        with open(config_file, 'r') as f:
            config = yaml.load(f, Loader=yaml.loader.SafeLoader)
        self.num_glb_banks = config['architecture']['num_glb_banks']
        self.num_pr = config['architecture']['num_pr']
        self.pr_height = config['architecture']['pr']['height']
        self.pr_width = config['architecture']['pr']['width']
        self.pr_num_input = config['architecture']['pr']['num_input']
        self.pr_num_output = config['architecture']['pr']['num_output']

    def print_config(self):
        print(f"num_glb_banks: {self.num_glb_banks}")

