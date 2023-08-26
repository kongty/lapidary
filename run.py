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
    parser.add_argument("--workload", type=str, default="./cfg/workload/workload_wddsa_edge.yml",
                        help="Path to the workload config file")
    # parser.add_argument("--workload", type=str, default="./cfg/workload/workload_1.yml",
    #                     help="Path to the workload config file")
    parser.add_argument("--log", action='store_true', help="Path to the log directory")
    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s', stream=sys.stdout, level=logging.DEBUG)

    app_pool = AppPool("app_pool_0")
    app_pool.add("rn_conv1", AppConfig(prr_shape=(1, 2), pe=150, mem=15, input=14, output=0, runtime=2458))
    app_pool.add("rn_conv1", AppConfig(prr_shape=(1, 4), pe=150, mem=15, input=14, output=0, runtime=1229))
    app_pool.add("rn_conv2", AppConfig(prr_shape=(1, 2), pe=150, mem=15, input=7, output=0, runtime=1806))
    app_pool.add("rn_conv2", AppConfig(prr_shape=(1, 6), pe=150, mem=15, input=7, output=0, runtime=452))
    app_pool.add("rn_conv3", AppConfig(prr_shape=(1, 2), pe=150, mem=15, input=4, output=0, runtime=903))
    app_pool.add("rn_conv3", AppConfig(prr_shape=(1, 6), pe=150, mem=15, input=4, output=0, runtime=226))
    app_pool.add("rn_conv4", AppConfig(prr_shape=(1, 2), pe=150, mem=15, input=6, output=0, runtime=903))
    app_pool.add("rn_conv4", AppConfig(prr_shape=(1, 6), pe=150, mem=15, input=6, output=0, runtime=226))
    app_pool.add("rn_conv5", AppConfig(prr_shape=(1, 2), pe=150, mem=15, input=20, output=0, runtime=903))
    app_pool.add("rn_conv5", AppConfig(prr_shape=(1, 6), pe=150, mem=15, input=20, output=0, runtime=226))

    app_pool.add("mn_conv1", AppConfig(prr_shape=(1, 2), pe=150, mem=15, input=4, output=0, runtime=610))
    app_pool.add("mn_conv1", AppConfig(prr_shape=(1, 5), pe=150, mem=15, input=4, output=0, runtime=141))
    app_pool.add("mn_conv2", AppConfig(prr_shape=(1, 2), pe=150, mem=15, input=4, output=0, runtime=573))
    app_pool.add("mn_conv2", AppConfig(prr_shape=(1, 5), pe=150, mem=15, input=4, output=0, runtime=132))
    app_pool.add("mn_conv3", AppConfig(prr_shape=(1, 2), pe=150, mem=15, input=4, output=0, runtime=115))
    app_pool.add("mn_conv3", AppConfig(prr_shape=(1, 3), pe=150, mem=15, input=4, output=0, runtime=573))
    app_pool.add("mn_conv4", AppConfig(prr_shape=(1, 2), pe=150, mem=15, input=4, output=0, runtime=554))
    app_pool.add("mn_conv4", AppConfig(prr_shape=(1, 3), pe=150, mem=15, input=4, output=0, runtime=278))
    app_pool.add("mn_conv5", AppConfig(prr_shape=(1, 2), pe=150, mem=15, input=4, output=0, runtime=545))
    app_pool.add("mn_conv6", AppConfig(prr_shape=(1, 3), pe=150, mem=15, input=4, output=0, runtime=272))
    app_pool.add("mn_conv6", AppConfig(prr_shape=(1, 2), pe=150, mem=15, input=4, output=0, runtime=109))
    app_pool.add("mn_conv5", AppConfig(prr_shape=(1, 3), pe=150, mem=15, input=4, output=0, runtime=545))
    app_pool.add("mn_conv7", AppConfig(prr_shape=(1, 2), pe=150, mem=15, input=5, output=0, runtime=540))
    app_pool.add("mn_conv7", AppConfig(prr_shape=(1, 5), pe=150, mem=15, input=5, output=0, runtime=125))

    app_pool.add("cp", AppConfig(prr_shape=(1, 2), pe=150, mem=15, input=4, output=0, runtime=2074))
    app_pool.add("cp", AppConfig(prr_shape=(1, 6), pe=150, mem=15, input=14, output=0, runtime=518))

    app_pool.add("harris", AppConfig(prr_shape=(1, 2), pe=150, mem=15, input=4, output=0, runtime=410))
    app_pool.add("harris", AppConfig(prr_shape=(1, 4), pe=150, mem=15, input=7, output=0, runtime=205))
    app_pool.add("harris", AppConfig(prr_shape=(1, 7), pe=150, mem=15, input=14, output=0, runtime=102))

    app_pool.add("stereo", AppConfig(prr_shape=(1, 1), pe=150, mem=15, input=3, output=0, runtime=2074))
    app_pool.add("stereo", AppConfig(prr_shape=(1, 2), pe=150, mem=15, input=6, output=0, runtime=1037))
    app_pool.add("stereo", AppConfig(prr_shape=(1, 4), pe=150, mem=15, input=9, output=0, runtime=520))
    app_pool.add("stereo", AppConfig(prr_shape=(1, 8), pe=150, mem=15, input=9, output=0, runtime=260))

    app_pool.add("gaussian", AppConfig(prr_shape=(1, 1), pe=192, mem=47, input=8, output=0, runtime=520))
    app_pool.add("gaussian", AppConfig(prr_shape=(1, 2), pe=150, mem=15, input=16, output=0, runtime=260))
    app_pool.add("gaussian", AppConfig(prr_shape=(1, 4), pe=150, mem=15, input=32, output=0, runtime=130))

    app_pool.add("app_0", AppConfig(prr_shape=(1, 1), pe=150, mem=15,
                 input=1, output=1, glb_size=10, offchip_bw=10, runtime=100))
    app_pool.add("app_1", AppConfig(prr_shape=(1, 2), pe=150, mem=15, input=1, output=1, runtime=170))

    lapidary = Lapidary(accelerator_config=args.arch, workload_config=args.workload, app_pool=app_pool)
    lapidary.run()
    if args.log:
        workload_name = os.path.basename(args.workload).rsplit('.', 1)[0]
        log_dir = os.path.join("logs", workload_name)
        lapidary.dump_logs(log_dir)
