import os
import yaml
import simpy
from typing import Optional, Union, Dict
from lapidary.task_generator import TaskGenerator
from functools import reduce
from lapidary.task_queue import TaskQueue


class Workload:
    def __init__(self, env: simpy.Environment, config: Optional[Union[str, Dict]] = None) -> None:
        self.env = env
        self.name = 'workload_0'
        self.task_generators = []
        if config is not None:
            self.set_workload(config)

    def set_workload(self, config: Union[str, Dict]) -> None:
        """Set workload properties with input configuration file."""
        if type(config) is str:
            if not os.path.exists(config):
                raise Exception("[ERROR] Workload config file not found")
            else:
                print(f"[LOG] Workload config file read: {config}")
            with open(config, 'r') as f:
                config = yaml.load(f, Loader=yaml.loader.SafeLoader)

        self.name = config['name']
        for task_config_dict in config["tasks"]:
            self.task_generators.append(TaskGenerator(self.env, task_config_dict))

    def run_dispatch(self, task_queue: TaskQueue) -> None:
        """Run task generate proccesses in each task generators."""
        for task_generator in self.task_generators:
            self.env.process(task_generator.proc_generate())
        self.env.process(self.dispatch(task_queue))

    def dispatch(self, task_queue: TaskQueue):
        """Run task generate proccesses in each task generators."""
        while True:
            evt_generate_list = [task_gen.evt_generate for task_gen in self.task_generators]
            evt_generate_any = reduce(lambda x, y: x | y, evt_generate_list)
            tasks_dict = yield evt_generate_any
            tasks = []
            for task_generator in self.task_generators:
                if task_generator.evt_generate in tasks_dict:
                    tasks.append(tasks_dict[task_generator.evt_generate])
                    task_generator.evt_generate = self.env.event()
            task_queue.put(tasks)
