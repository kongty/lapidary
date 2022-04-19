import simpy
from abc import ABC, abstractmethod
from lapidary.accelerator import Accelerator
from lapidary.task import Task
from lapidary.task_queue import TaskQueue
from lapidary.app import AppPool
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
            # print(f"[@ {self.env.now}] schedule is triggered.")
            for _ in range(self.task_queue.size()):
                # Get one task from a queue and schedule it on the accelerator.
                task = self.task_queue.peek()
                if self.schedule(task, accelerator, app_pool):
                    print(f"[@ {self.env.now}] {task.name} is scheduled.")
                    self.task_queue.get()

    def schedule(self, task: Task, accelerator: Accelerator, app_pool: AppPool) -> bool:
        """Schedule a task on the accelerator and returns True/False if scheduling succeeds/fails."""
        task_app_config_list = app_pool.get(task.app)
        # TODO: Optimize by choosing the best bitstream from the app_pool.
        # For now, we just use the first app_config from the app_pool.
        if len(task_app_config_list) == 0:
            print(f"[LOG] There is no app_config for {task.app} in the app_pool. This task will be dropped.")
            self.task_queue.get()
            return False

        app_config = task_app_config_list[0]
        task.set_app_config(app_config)

        prs = accelerator.map(task)
        if len(prs) == 0:
            print(f"[@ {self.env.now}] Cannot map {task.name} on the accelerator yet.")
            return False

        accelerator.execute(task, prs)

        return True
