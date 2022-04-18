from lapidary.accelerator import Accelerator
from lapidary.workload import Workload
from lapidary.scheduler import Scheduler
from lapidary.app_pool import AppPool
import simpy


class Simulator:
    def __init__(self, env: simpy.Environment, accelerator: Accelerator, workload: Workload, scheduler: Scheduler,
                 app_pool: AppPool) -> None:
        self.env = env
        self.accelerator = accelerator
        self.workload = workload
        self.scheduler = scheduler
        self.app_pool = app_pool

    def run(self, until: int) -> None:
        self.workload.run_dispatch(self.scheduler.task_queue)
        self.scheduler.run(self.accelerator, self.app_pool)

        self.env.run(until=until)
