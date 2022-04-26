import argparse
from lapidary.app import AppConfig, AppPool
from lapidary.lapidary import Lapidary
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
    app_pool.add("app_0", AppConfig(pr_shape=(1, 4), pe=150, mem=15, input=1, output=1, runtime=100))
    app_pool.add("app_1", AppConfig(pr_shape=(1, 8), pe=150, mem=15, input=1, output=1, runtime=50))

    lapidary = Lapidary(accelerator_config=args.arch, workload_config=args.workload, app_pool=app_pool)
    lapidary.run(until=2000)
