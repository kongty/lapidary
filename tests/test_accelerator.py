import simpy
import pytest
from typing import Tuple
from lapidary.accelerator import Accelerator, AcceleratorConfigType
from lapidary.app import AppConfig

accelerator_config = AcceleratorConfigType(
    {
        'name': 'accelerator',
        'num_glb_banks': 32,
        'num_prr_height': 4,
        'num_prr_width': 4,
        'prr': {
            'height': 8,
            'width': 8,
            'num_input': 4,
            'num_output': 4
        }
    }
)


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
