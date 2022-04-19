import pytest
import simpy
from lapidary.accelerator import Accelerator
from lapidary.workload import Workload
from lapidary.scheduler import GreedyScheduler
from lapidary.app import AppPool, AppConfig


# Global accelerator config
accelerator_config = {
    'name': 'accelerator_0',
    'num_glb_banks': 32,
    'num_pr_height': 1,
    'num_pr_width': 8,
    'pr_flexible': False,
    'pr': {'height': 16, 'width': 4, 'num_input': 4, 'num_output': 4}
}

# Global app_pool
app_pool = AppPool("app_pool_0")
app_pool.add("app_0", AppConfig(pr_shape=(1, 4), pe=150, mem=15, input=1, output=1, runtime=100))
app_pool.add("app_1", AppConfig(pr_shape=(1, 8), pe=150, mem=15, input=1, output=1, runtime=50))


# @pytest.mark.parametrize()
def test_greedy_scheduler():
    env = simpy.Environment()
    accelerator = Accelerator(env, accelerator_config)
    workload = Workload(env, workload_config)
    scheduler = GreedyScheduler(env)
    scheduler.set_app_pool(app_pool)

    workload.run_dispatch(scheduler.task_queue)
    scheduler.run(accelerator)
    breakpoint()
    env.run(500)
