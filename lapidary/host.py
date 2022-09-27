import simpy


class Host:
    def __init__(self, env: simpy.Environment) -> None:
        self.env = env
