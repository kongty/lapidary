from lapidary.hardware import Hardware
from lapidary.workload import Workload
from lapidary.scheduler import Scheduler
import simpy


class Simulator:
    def __init__(self, env: simpy.Environment, hardware: Hardware, workload: Workload, scheduler: Scheduler) -> None:
        self.env = env
        self.hardware = hardware
        self.workload = workload
        self.scheduler = scheduler

    def run(self, until: int) -> None:
        self.workload.run_dispatch(self.scheduler.task_queue)
        self.scheduler.run(self.hardware)

        self.env.run(until=until)
