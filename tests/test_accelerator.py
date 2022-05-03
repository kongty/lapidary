import simpy
import pytest
from typing import Tuple
from lapidary.accelerator import Accelerator
from lapidary.app import AppConfig

accelerator_config = {
    'name': 'accelerator',
    'num_glb_banks': 32,
    'num_pr_height': 4,
    'num_pr_width': 4,
    'offchip_bandwidth': 256,
    'noc_bandwidth': 256,
    'pr': {
        'height': 8,
        'width': 8,
        'num_input': 4,
        'num_output': 4
    }
}


@pytest.mark.parametrize('shape', [(2, 2), (4, 4), (1, 3), (3, 1)])
def test_accelerator_map(shape: Tuple[int, int]):
    env = simpy.Environment()
    accelerator = Accelerator(env, accelerator_config)

    width, height = shape
    app_config = AppConfig(pr_shape=(width, height))
    prs = accelerator.map(app_config)
    assert len(prs) == width * height

    idx = 0
    for j in range(width):
        for i in range(height):
            assert prs[idx].id == (i, j)
            idx += 1


def test_accelerator_allocate():
    pass


def test_accelerator_deallocate():
    pass


def test_accelerator_execute():
    pass
