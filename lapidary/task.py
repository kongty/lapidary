from lapidary.task_generator_config import TaskGeneratorConfig


class Task:
    def __init__(self, id: int, config: TaskGeneratorConfig) -> None:
        self.id = id
        self.config = config
        self.ts_arrival = 0
        self.ts_schedule = 0
        self.ts_done = 0
