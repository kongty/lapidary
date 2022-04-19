import argparse
from lapidary.app_config import AppConfig
from lapidary.lapidary import Lapidary
from lapidary.app_pool import AppPool
import numpy as np
np.random.seed(10)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CGRA simulation")
    parser.add_argument("--arch", metavar="arch file", type=str,
                        default="./cfg/hw/amber.yml", help="Path to the architecture config file")
    parser.add_argument("--workload", metavar="workload file", type=str,
                        default="./cfg/workload/workload_0.yml", help="Path to the workload config file")
    parser.add_argument("--log-dir", metavar="log dir", type=str, default="./logs", help="Path to log directory")
    args = parser.parse_args()

    app_pool = AppPool("app_pool_0")
    # TODO: For now, we only use pr/input/output for scheduling.
    app_pool.add("app_0", AppConfig(pr_shape=(1, 4), pe=150, mem=15, input=1, output=1, runtime=100))
    app_pool.add("app_1", AppConfig(pr_shape=(1, 8), pe=150, mem=15, input=1, output=1, runtime=50))

    lapidary = Lapidary(architecture_filename=args.arch, workload_filename=args.workload, app_pool=app_pool)
    lapidary.run(until=1000)
