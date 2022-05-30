import simpy
import pytest
from typing import Tuple
from lapidary.accelerator import Accelerator
from lapidary.app import AppConfig
from .test_configs import accelerator_config


@pytest.mark.parametrize('shape', [(2, 2), (4, 4), (1, 3), (3, 1)])
def test_accelerator_map(shape: Tuple[int, int]):
    env = simpy.Environment()
    accelerator = Accelerator(env, accelerator_config)

    width, height = shape
    app_config = AppConfig(prr_shape=(width, height))
    prrs = accelerator.map(app_config)
    assert len(prrs) == width * height

    idx = 0
    for j in range(width):
        for i in range(height):
            assert prrs[idx].id == (i, j)
            idx += 1


def test_accelerator_allocate():
    pass


def test_accelerator_deallocate():
    pass


def test_accelerator_execute():
    pass
