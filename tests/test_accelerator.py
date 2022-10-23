import simpy
import pytest
from typing import Tuple
from lapidary.accelerator import Accelerator
from lapidary.app import LayerConfig
from .test_configs import accelerator_config


@pytest.mark.parametrize('shape', [(2, 2), (4, 4), (1, 3), (3, 1)])
def test_accelerator_map(shape: Tuple[int, int]):
    env = simpy.Environment()
    accelerator = Accelerator(env, accelerator_config)

    height, width = shape
    app_config = LayerConfig(core_shape=(height, width))
    prrs = accelerator.map(app_config)
    assert len(prrs) == width * height

    idx = 0
    for i in range(height):
        for j in range(width):
            assert prrs[idx].id == i * accelerator.config.num_prr_width + j
            idx += 1


def test_accelerator_allocate():
    pass


def test_accelerator_deallocate():
    pass


def test_accelerator_execute():
    pass
