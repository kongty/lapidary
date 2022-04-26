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
        self.log_tasks = []
        self.app_pool = None

    def set_app_pool(self, app_pool: AppPool) -> None:
        self.app_pool = app_pool

    def run(self, accelerator: Accelerator) -> None:
        self.env.process(self.proc_schedule(accelerator))

    @abstractmethod
    def proc_schedule(self, accelerator: Accelerator) -> None:
        pass

    @abstractmethod
    def schedule(self, accelerator: Accelerator) -> List[Task]:
        pass


class GreedyScheduler(Scheduler):
    def __init__(self, env: simpy.Environment) -> None:
        super().__init__(env)

    def proc_schedule(self, accelerator: Accelerator) -> None:
        """Call schedule function when new tasks arrive or old tasks finish."""
        while True:
            triggered = yield self.task_queue.evt_task_arrive | accelerator.evt_task_done
            if self.task_queue.evt_task_arrive in triggered:
                self.log_tasks.extend(triggered[self.task_queue.evt_task_arrive])
                self.task_queue.acknowledge()
            if accelerator.evt_task_done in triggered:
                task = triggered[accelerator.evt_task_done]
                self.task_queue.update_dependency(done=task)
                accelerator.acknowledge_task_done()
            self.schedule(accelerator)

    def schedule(self, accelerator: Accelerator) -> List[Task]:
        """Schedule tasks on the accelerator and return a list of tasks that are scheduled."""
        for task in self.task_queue.q:
            # Get one task from a queue that is dependency-free
            if len(task.deps) == 0:
                # TODO: Optimize by choosing the best bitstream from the app_pool.
                # For now, we just use the first app_config from the app_pool.
                app_config_list = self.app_pool.get(task.app)
                if len(app_config_list) == 0:
                    print(f"[LOG] There is no app_config for {task.app} in the app_pool. This task will be dropped.")
                    self.task_queue.remove(task)

                app_config = app_config_list[0]
                task.set_app_config(app_config)

                prs = accelerator.map(task)
                if len(prs) == 0:
                    print(f"[@ {self.env.now}] Cannot map {task.tag} on the accelerator yet.")
                    return False

                print(f"[@ {self.env.now}] {task.tag} is scheduled.")
                task.ts_schedule = self.env.now
                self.task_queue.get()


        accelerator.execute(task, prs)

        return True
