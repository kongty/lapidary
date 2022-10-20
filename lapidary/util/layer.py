import maestro
from maestro import LayerDimension
from dataclasses import dataclass
from abc import ABC
from enum import Enum


class Dataflow(Enum):
    NVDLA = 1


class Layer:
    def __init__(self, name: str, k: int, c: int, r: int, s: int, y: int, x: int, stride: int = 1):
        self.name = name
        self.k = k
        self.c = c
        self.r = r
        self.s = s
        self.y = y
        self.x = x
        self.stride = stride

    def set_dataflow(self, dataflow: Dataflow, pes_per_core: int):
        if dataflow is Dataflow.NVDLA:
            directives = maestro.DirectiveTable([maestro.SpatialMap(1, 1, "K"),
                                                 maestro.TemporalMap(pes_per_core, pes_per_core, "C"),
                                                 maestro.TemporalMap(self.r, self.s, "R"),
                                                 maestro.TemporalMap(self.s, self.s, "S"),
                                                 maestro.TemporalMap(self.r, 1, "Y"),
                                                 maestro.TemporalMap(self.s, 1, "X"),
                                                 maestro.Cluster(pes_per_core, maestro.ClusterType.Physical),
                                                 maestro.SpatialMap(1, 1, "C"),
                                                 maestro.TemporalMap(self.r, 1, "Y"),
                                                 maestro.TemporalMap(self.s, 1, "X"),
                                                 maestro.TemporalMap(self.r, self.s, "R"),
                                                 maestro.TemporalMap(self.s, self.s, "S")])
            self.set_directives(directives)
        else:
            raise NotImplementedError("Dataflow other than NVDLA is not implemented.")


class ConvLayer(Layer, maestro.ConvLayer):
    def __init__(self, name: str, k: int, c: int, r: int, s: int, y: int, x: int, stride: int = 1):
        super().__init__(name, k, c, r, s, y, x, stride)
        dimensions = [LayerDimension('K', self.k, 1, 1),
                      LayerDimension('C', self.c, 1, 1),
                      LayerDimension('R', self.r, 1, 1),
                      LayerDimension('S', self.s, 1, 1),
                      LayerDimension('Y', self.y, self.stride, 1),
                      LayerDimension('X', self.x, self.stride, 1),
                      ]
        maestro.ConvLayer.__init__(self, name, dimensions)


class DSConvLayer(maestro.DSConvLayer):
    def __init__(self, name: str, k: int, c: int, r: int, s: int, y: int, x: int, stride: int = 1):
        dimensions = [LayerDimension('K', k, 1, 1),
                      LayerDimension('C', c, 1, 1),
                      LayerDimension('R', r, 1, 1),
                      LayerDimension('S', s, 1, 1),
                      LayerDimension('Y', y, stride, 1),
                      LayerDimension('X', x, stride, 1),
                      ]
        super(DSConvLayer, self).__init__(name, dimensions)


class Network(ABC):
    def __init__(self):
        self.layers = []

    def add(self, layer: maestro.Layer):
        pass


class MyNetwork(Network):
    def __init__(self):
        self.layers = []
        # self.layers.append(ConvLayer("conv_2_1_1", 64, 64, 1, 1, 56, 56, 1))
        self.layers.append(ConvLayer("conv_2_1_2", 64, 64, 3, 3, 56, 56, 1))


@dataclass(frozen=True)
class EnergyTable:
    l1_rd_energy: float
    l1_wr_energy: float
    l2_rd_energy: float
    l2_wr_energy: float
    mac_energy: float
    noc_energy: float
    offchip_rd_energy: float
    offchip_wr_energy: float

# class SubAccelerator(maestro.SubAccelerator):
#     def __init__(self, num_pe, simd, l1_size, l2_size, offchip_bw, noc_bw, noc_multicast: bool = True):
#         self.num_pe = num_pe
#         self.l1_size = l1_size
#         self.l2_size = l2_size
#         self.simd = simd
#         self.offchip_bw = offchip_bw
#         # Maestro takes vector of bandwidth and multicast. However, it only uses the top one.
#         self.noc_bw = [noc_bw, noc_bw]
#         self.noc_multicast = [noc_multicast, noc_multicast]
#         self.noc_latency = [1, 1]
#         super().__init__(self.num_pe, self.simd, self.l1_size, self.l2_size, self.offchip_bw, self.noc_bw,
#                          self.noc_latency, self.noc_multicast)

class SubAccelerator(maestro.SubAccelerator):
    # def __init__(self, num_pe, simd, l1_size, l2_size, offchip_bw, noc_bw, noc_multicast: bool = True):
    def __init__(self, num_pe, l1_size, l2_size, offchip_bw):
        self.num_pe = num_pe
        self.l1_size = l1_size
        self.l2_size = l2_size
        self.offchip_bw = offchip_bw
        # super().__init__(self.num_pe, 1, int(self.l1_size/self.num_pe), self.l2_size, 1, [1, 1], [1, 1], [True, True])
        super().__init__(self.num_pe, 1, int(self.l1_size/self.num_pe), self.l2_size, self.offchip_bw, [1, 100], [1, 1], [True, True])
        # self.simd = simd
        # Maestro takes vector of bandwidth and multicast. However, it only uses the top one.
        # self.noc_bw = [noc_bw, noc_bw]
        # self.noc_multicast = [noc_multicast, noc_multicast]
        # self.noc_latency = [1, 1]
        # super().__init__(self.num_pe, self.simd, self.l1_size, self.l2_size, self.offchip_bw, self.noc_bw,
        #                  self.noc_latency, self.noc_multicast)


class Metric(Enum):
    LATENCY = 1
    ENERGY = 2
    EDP = 3


@dataclass(frozen=True)
class CostResult:
    valid: bool
    latency: int
    energy: float
    edp: float
    l1_energy: float
    l2_energy: float
    offchip_bw: float


class CostModel:
    def __init__(self, energy_table: EnergyTable):
        self.energy_table = energy_table

    def run(self, subaccelerator: SubAccelerator, layer: Layer, dataflow: Dataflow) -> CostResult:
        layer.set_dataflow(dataflow, pes_per_core=64)
        result = maestro.run(subaccelerator, layer)
        if result['l1_size'] <= subaccelerator.l1_size and result['l2_size'] <= subaccelerator.l2_size:
            valid = True
        else:
            valid = False

        latency = result['runtime']
        l1_energy = result['l1_rd_count'] * self.energy_table.l1_rd_energy + \
            result['l1_wr_count'] * self.energy_table.l1_wr_energy
        l2_energy = result['l2_rd_count'] * self.energy_table.l2_rd_energy + \
            result['l2_wr_count'] * self.energy_table.l2_wr_energy
        energy = l1_energy + l2_energy
        cost_result = CostResult(valid=valid, latency=latency, energy=energy, edp=latency*energy, l1_energy=l1_energy,
                                 l2_energy=l2_energy, offchip_bw=result['offchip_bw'])
        return cost_result
