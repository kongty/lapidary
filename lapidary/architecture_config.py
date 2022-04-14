class ArchitectureConfig:
    def __init__(self) -> None:
        self.name = 'amber'
        self.num_glb_banks = 32
        self.num_pr = 8
        self.pr_flexible = False
        self.pr_height = 16
        self.pr_width = 4
        self.pr_num_input = 4
        self.pr_num_output = 4

    def set_config(self, config_dict: dict) -> None:
        self.name = config_dict['name']
        self.num_glb_banks = config_dict['num_glb_banks']
        self.num_pr = config_dict['num_pr']
        self.pr_flexible = config_dict['pr_flexible']
        self.pr_height = config_dict['pr']['height']
        self.pr_width = config_dict['pr']['width']
        self.pr_num_input = config_dict['pr']['num_input']
        self.pr_num_output = config_dict['pr']['num_output']
