import argparse
from lapidary.app import LayerConfig, DNNPool
from lapidary.lapidary import Lapidary
import numpy as np
import logging
import sys
import os
from lapidary.util.layer import CostModel, Dataflow, EnergyTable, MyNetwork, SubAccelerator

np.random.seed(10)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CGRA simulation")
    parser.add_argument("--arch", type=str, default="./cfg/hw/amber.yml", help="Path to the architecture config file")
    parser.add_argument("--workload", type=str, default="./cfg/workload/workload_wddsa_edge.yml",
                        help="Path to the workload config file")

    # parser.add_argument("--workload", type=str, default="./cfg/workload/workload_1.yml",
    #                     help="Path to the workload config file")

    parser.add_argument("--log", action='store_true', help="Path to the log directory")
    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s', stream=sys.stdout, level=logging.DEBUG)

    nn = MyNetwork()
    energy_table = EnergyTable(l1_rd_energy=1.68,
                               l1_wr_energy=1.68,
                               l2_rd_energy=18.61,
                               l2_wr_energy=18.61,
                               mac_energy=1,
                               noc_energy=1,
                               offchip_rd_energy=30,
                               offchip_wr_energy=30)

    subaccelerator = SubAccelerator(256, 2560, 100, 100)
    # subaccelerator = SubAccelerator(256, 1, 10, 100, 100, 100, True)
    cost_model = CostModel(energy_table)
    layer_result = cost_model.run(subaccelerator, nn.layers[0], Dataflow.NVDLA)
    print(layer_result)

    # dnn_pool = DNNPool("app_pool_0")

    # lapidary = Lapidary(accelerator_config=args.arch, workload_config=args.workload, app_pool=dnn_pool)
    # lapidary.run()
    # if args.log:
    #     workload_name = os.path.basename(args.workload).rsplit('.', 1)[0]
    #     log_dir = os.path.join("logs", workload_name)
    #     lapidary.dump_logs(log_dir)
