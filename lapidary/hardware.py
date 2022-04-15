from lapidary.architecture import Architecture
import simpy


class Hardware:
    def __init__(self, env: simpy.Environment, architecture: Architecture) -> None:
        self.env = env
        self.architecture = architecture
        self.pr = [0] * self.architecture.num_pr