import pytest
import simpy
from lapidary.accelerator import Accelerator
from lapidary.workload import Workload
from lapidary.scheduler import GreedyScheduler
from lapidary.app import AppPool, AppConfig
from typing import List


# Global accelerator config
accelerator_config = {
    'name': 'accelerator_0',
    'num_glb_banks': 32,
    'num_pr_height': 1,
    'num_pr_width': 8,
    'pr_flexible': False,
    'pr': {'height': 16, 'width': 4, 'num_input': 4, 'num_output': 4}
}


@pytest.mark.parametrize('task_interval', [[50, 50], [200, 200]])
@pytest.mark.parametrize('runtime', [50, 100])
def test_greedy_scheduler(task_interval: List[int], runtime: int):
    # Create environment
    env = simpy.Environment()

    # Create accelerator
    accelerator = Accelerator(env, accelerator_config)

    # Create workload
    app_name = 'app_0'
    task = {'name': 'task_0', 'app': app_name, 'dist': 'manual', 'dist_start': 0, 'dist_interval': task_interval}
    workload = {'name': 'workload', 'tasks': [task]}
    workload = Workload(env, workload)

    # Create app_pool
    app_pool = AppPool("app_pool")
    app_pool.add(app_name, AppConfig(pr_shape=(accelerator.config.num_pr_height,
                 accelerator.config.num_pr_width), pe=150, mem=15, input=1, output=1, runtime=runtime))

    # Create greedy scheduler
    scheduler = GreedyScheduler(env)
    scheduler.set_app_pool(app_pool)

    # Start simulation
    workload.run_dispatch(scheduler.task_queue)
    scheduler.run(accelerator)
    env.run(600)

    assert scheduler.task_log[0].ts_arrive == task_interval[0]
    assert scheduler.task_log[0].ts_schedule == task_interval[0]
    assert scheduler.task_log[0].ts_done == task_interval[0] + runtime

    assert scheduler.task_log[1].ts_arrive == task_interval[0] + task_interval[1]
    assert scheduler.task_log[1].ts_schedule == max(task_interval[0] + task_interval[1], task_interval[0] + runtime)
    assert scheduler.task_log[1].ts_done == max(
        task_interval[0] + task_interval[1], task_interval[0] + runtime) + runtime
