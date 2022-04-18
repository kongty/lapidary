import simpy


class Task:
    def __init__(self, env: simpy.Environment, task: str, id: int, app: str) -> None:
        self.env = env
        self.task = task
        self.id = id
        self.name = self.task + "_#" + str(self.id)
        self.app = app
        self.ts_arrive = 0
        self.ts_schedule = 0
        self.ts_done = 0

    def proc_execute(self, runtime: int) -> None:
        print(f"{self.name} execution starts @ {self.env.now}.")
        yield self.env.timeout(runtime)
        print(f"{self.name} execution finishes @ {self.env.now}.")
        self.ts_done = self.env.now
