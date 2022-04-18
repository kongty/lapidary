import simpy
from abc import ABC, abstractmethod
from lapidary.accelerator import Accelerator
from lapidary.task import Task
from lapidary.task_queue import TaskQueue
from lapidary.app_pool import AppPool
from typing import List


class Scheduler(ABC):
    def __init__(self, env: simpy.Environment) -> None:
        self.env = env
        self.task_queue = TaskQueue(self.env)

    def run(self, accelerator: Accelerator, app_pool: AppPool) -> None:
        self.env.process(self.proc_schedule(accelerator, app_pool))

    @abstractmethod
    def proc_schedule(self, accelerator: Accelerator, app_pool: AppPool) -> None:
        pass

    @abstractmethod
    def schedule(self, tasks: List[Task], accelerator: Accelerator, app_pool: AppPool) -> bool:
        pass


class GreedyScheduler(Scheduler):
    def __init__(self, env: simpy.Environment) -> None:
        super().__init__(env)

    def proc_schedule(self, accelerator: Accelerator, app_pool: AppPool) -> None:
        """Call schedule function when new tasks arrive or old tasks finish."""
        while True:
            yield self.task_queue.evt_task_arrive | accelerator.evt_task_done
            print(f"schedule is triggered @ {self.env.now}")
            for _ in range(self.task_queue.size()):
                # Get one task from a queue and schedule it on the accelerator.
                task = self.task_queue.get()
                self.schedule([task], accelerator, app_pool)
                print(f"{task.name} is scheduled @ {self.env.now}")

    def schedule(self, tasks: List[Task], accelerator: Accelerator, app_pool: AppPool) -> bool:
        """Schedule tasks on the accelerator and returns True/False if scheduling succeeds/fails."""
        for task in tasks:
            task_app_config_list = app_pool.get(task.app)
            # TODO: Optimize by choosing the best bitstream from the app_pool.
            # For now, we just use the first app_config from the app_pool.
            app_config = task_app_config_list[0]
            # lb_point, rt_point = accelerator.get_max_rectangle_prs()
            accelerator.execute(task, app_config, None)
