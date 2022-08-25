import argparse
from lapidary.app import AppConfig, AppPool
from lapidary.lapidary import Lapidary
import numpy as np
import logging
import sys
import os
np.random.seed(10)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CGRA simulation")
    parser.add_argument("--arch", type=str, default="./cfg/hw/amber.yml", help="Path to the architecture config file")
    parser.add_argument("--workload", type=str, default="./cfg/workload/workload_wddsa.yml",
                        help="Path to the workload config file")
    parser.add_argument("--log", action='store_true', help="Path to the log directory")
    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s', stream=sys.stdout, level=logging.INFO)

    app_pool = AppPool("app_pool_0")
    app_pool.add("app_0", AppConfig(prr_shape=(1, 1), pe=150, mem=15, input=1, output=1, runtime=100))
    app_pool.add("app_1", AppConfig(prr_shape=(1, 2), pe=150, mem=15, input=2, output=3, runtime=50))

    lapidary = Lapidary(accelerator_config=args.arch, workload_config=args.workload, app_pool=app_pool)
    lapidary.run(until=7000)
    if args.log:
        workload_name = os.path.basename(args.workload).rsplit('.', 1)[0]
        log_dir = os.path.join("logs", workload_name)
        lapidary.dump_logs(log_dir)
