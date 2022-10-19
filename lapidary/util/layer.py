import maestro
from maestro import LayerDimension


from abc import ABC


def ConvLayer(name: str, k: int, c: int, r: int, s: int, y: int, x: int, stride: int = 1):
    dimensions = [LayerDimension('K', k, 1, 1),
                  LayerDimension('C', c, 1, 1),
                  LayerDimension('R', r, 1, 1),
                  LayerDimension('S', s, 1, 1),
                  LayerDimension('Y', y, stride, 1),
                  LayerDimension('X', x, stride, 1),
                  ]
    return maestro.ConvLayer(name, dimensions)


class Network(ABC):
    def __init__(self):
        self.layers = []

    def add(self, layer: maestro.Layer):
        pass


class MyNetwork(Network):
    def __init__(self):
        self.layers = []
        self.layers.append(ConvLayer("conv_2_1_1", 64, 64, 1, 1, 56, 56, 1))
        self.layers.append(ConvLayer("conv_1_2", 64, 64, 3, 3, 56, 56, 1))
