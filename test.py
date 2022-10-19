import argparse
from lapidary.app import LayerConfig, DNNPool
from lapidary.lapidary import Lapidary
import numpy as np
import logging
import sys
import os
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

    dnn_pool = DNNPool("app_pool_0")

    lapidary = Lapidary(accelerator_config=args.arch, workload_config=args.workload, app_pool=dnn_pool)
    lapidary.run()
    if args.log:
        workload_name = os.path.basename(args.workload).rsplit('.', 1)[0]
        log_dir = os.path.join("logs", workload_name)
        lapidary.dump_logs(log_dir)
