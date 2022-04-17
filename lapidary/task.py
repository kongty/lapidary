import simpy
from lapidary.task_generator_config import TaskGeneratorConfig


class Task:
    def __init__(self, env: simpy.Environment, id: int, config: TaskGeneratorConfig) -> None:
        self.env = env
        self.id = id
        self.config = config
        self.name = self.config.name + "_" + str(self.id)
        self.ts_arrive = 0
        self.ts_schedule = 0
        self.ts_done = 0

    def execute(self) -> None:
        print(f"Task {self.name} execution starts @ {self.env.now}.")
        yield self.env.timeout(self.config.runtime)
        print(f"Task {self.name} execution finishes @ {self.env.now}.")
        self.ts_done = self.env.now
