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
    # parser.add_argument("--workload", type=str, default="./cfg/workload/workload_1.yml",
    #                     help="Path to the workload config file")
    parser.add_argument("--log", action='store_true', help="Path to the log directory")
    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s', stream=sys.stdout, level=logging.INFO)

    app_pool = AppPool("app_pool_0")
    app_pool.add("rn_conv2", AppConfig(prr_shape=(1, 1), glb=2,  runtime=8508))
    app_pool.add("rn_conv2", AppConfig(prr_shape=(1, 2), glb=6,  runtime=2127))
    app_pool.add("rn_conv2", AppConfig(prr_shape=(1, 4), glb=8,  runtime=1064))
    app_pool.add("rn_conv2", AppConfig(prr_shape=(1, 6), glb=8,  runtime=532))

    app_pool.add("rn_conv3", AppConfig(prr_shape=(1, 1), glb=2,  runtime=8730))
    app_pool.add("rn_conv3", AppConfig(prr_shape=(1, 2), glb=6,  runtime=2182))
    app_pool.add("rn_conv3", AppConfig(prr_shape=(1, 4), glb=8,  runtime=1091))
    app_pool.add("rn_conv3", AppConfig(prr_shape=(1, 6), glb=8,  runtime=546))

    app_pool.add("rn_conv4", AppConfig(prr_shape=(1, 1), glb=2,  runtime=8501))
    app_pool.add("rn_conv4", AppConfig(prr_shape=(1, 2), glb=6,  runtime=2125))
    app_pool.add("rn_conv4", AppConfig(prr_shape=(1, 4), glb=8,  runtime=1063))
    app_pool.add("rn_conv4", AppConfig(prr_shape=(1, 6), glb=8,  runtime=531))

    app_pool.add("rn_conv5", AppConfig(prr_shape=(1, 1), glb=2,  runtime=10904))
    app_pool.add("rn_conv5", AppConfig(prr_shape=(1, 2), glb=6,  runtime=2726))
    app_pool.add("rn_conv5", AppConfig(prr_shape=(1, 4), glb=8,  runtime=1363))
    app_pool.add("rn_conv5", AppConfig(prr_shape=(1, 6), glb=8,  runtime=682))


    app_pool.add("mn_conv2_pw", AppConfig(prr_shape=(1, 6), glb=8,  runtime=161))
    app_pool.add("mn_conv2_pw", AppConfig(prr_shape=(1, 2), glb=2,  runtime=483))
    app_pool.add("mn_conv2_dw", AppConfig(prr_shape=(1, 6), glb=4,  runtime=159))
    app_pool.add("mn_conv2_pw2", AppConfig(prr_shape=(1, 6), glb=8,  runtime=64))
    app_pool.add("mn_conv2_pw2", AppConfig(prr_shape=(1, 2), glb=2,  runtime=192))

    app_pool.add("mn_conv3_pw", AppConfig(prr_shape=(1, 6), glb=8,  runtime=96))
    app_pool.add("mn_conv3_pw", AppConfig(prr_shape=(1, 2), glb=2,  runtime=288))
    app_pool.add("mn_conv3_dw", AppConfig(prr_shape=(1, 2), glb=4,  runtime=80))
    app_pool.add("mn_conv3_pw2", AppConfig(prr_shape=(1, 6), glb=8,  runtime=96))
    app_pool.add("mn_conv3_pw2", AppConfig(prr_shape=(1, 2), glb=2,  runtime=288))

    app_pool.add("mn_conv4_pw", AppConfig(prr_shape=(1, 6), glb=8,  runtime=96))
    app_pool.add("mn_conv4_pw", AppConfig(prr_shape=(1, 2), glb=2,  runtime=288))
    app_pool.add("mn_conv4_dw", AppConfig(prr_shape=(1, 2), glb=4,  runtime=60))
    app_pool.add("mn_conv4_pw2", AppConfig(prr_shape=(1, 6), glb=8,  runtime=36))
    app_pool.add("mn_conv4_pw2", AppConfig(prr_shape=(1, 2), glb=2,  runtime=108))

    app_pool.add("mn_conv5_pw", AppConfig(prr_shape=(1, 6), glb=8,  runtime=48))
    app_pool.add("mn_conv5_pw", AppConfig(prr_shape=(1, 2), glb=2,  runtime=144))
    app_pool.add("mn_conv5_dw", AppConfig(prr_shape=(1, 2), glb=4,  runtime=35))
    app_pool.add("mn_conv5_pw2", AppConfig(prr_shape=(1, 6), glb=8,  runtime=48))
    app_pool.add("mn_conv5_pw2", AppConfig(prr_shape=(1, 2), glb=2,  runtime=144))

    app_pool.add("mn_conv6_pw", AppConfig(prr_shape=(1, 6), glb=8,  runtime=48))
    app_pool.add("mn_conv6_pw", AppConfig(prr_shape=(1, 2), glb=2,  runtime=144))
    app_pool.add("mn_conv6_dw", AppConfig(prr_shape=(1, 2), glb=4,  runtime=35))
    app_pool.add("mn_conv6_pw2", AppConfig(prr_shape=(1, 6), glb=8,  runtime=48))
    app_pool.add("mn_conv6_pw2", AppConfig(prr_shape=(1, 2), glb=2,  runtime=144))

    app_pool.add("mn_conv7_pw", AppConfig(prr_shape=(1, 6), glb=8,  runtime=48))
    app_pool.add("mn_conv7_pw", AppConfig(prr_shape=(1, 2), glb=2,  runtime=144))
    app_pool.add("mn_conv7_dw", AppConfig(prr_shape=(1, 2), glb=4,  runtime=22))
    app_pool.add("mn_conv7_pw2", AppConfig(prr_shape=(1, 6), glb=8,  runtime=20))
    app_pool.add("mn_conv7_pw2", AppConfig(prr_shape=(1, 2), glb=2,  runtime=60))

    app_pool.add("mn_conv8_pw", AppConfig(prr_shape=(1, 6), glb=8,  runtime=41))
    app_pool.add("mn_conv8_pw", AppConfig(prr_shape=(1, 2), glb=2,  runtime=123))
    app_pool.add("mn_conv8_dw", AppConfig(prr_shape=(1, 2), glb=4,  runtime=26))
    app_pool.add("mn_conv8_pw2", AppConfig(prr_shape=(1, 6), glb=8,  runtime=41))
    app_pool.add("mn_conv8_pw2", AppConfig(prr_shape=(1, 2), glb=2,  runtime=123))

    app_pool.add("mn_conv9_pw", AppConfig(prr_shape=(1, 6), glb=8,  runtime=41))
    app_pool.add("mn_conv9_pw", AppConfig(prr_shape=(1, 2), glb=2,  runtime=123))
    app_pool.add("mn_conv9_dw", AppConfig(prr_shape=(1, 2), glb=4,  runtime=26))
    app_pool.add("mn_conv9_pw2", AppConfig(prr_shape=(1, 6), glb=8,  runtime=41))
    app_pool.add("mn_conv9_pw2", AppConfig(prr_shape=(1, 2), glb=2,  runtime=123))

    app_pool.add("mn_conv10_pw", AppConfig(prr_shape=(1, 6), glb=8,  runtime=41))
    app_pool.add("mn_conv10_pw", AppConfig(prr_shape=(1, 2), glb=2,  runtime=123))
    app_pool.add("mn_conv10_dw", AppConfig(prr_shape=(1, 2), glb=4,  runtime=26))
    app_pool.add("mn_conv10_pw2", AppConfig(prr_shape=(1, 6), glb=8,  runtime=41))
    app_pool.add("mn_conv10_pw2", AppConfig(prr_shape=(1, 2), glb=2,  runtime=123))

    app_pool.add("mn_conv11_pw", AppConfig(prr_shape=(1, 6), glb=8,  runtime=41))
    app_pool.add("mn_conv11_pw", AppConfig(prr_shape=(1, 2), glb=2,  runtime=123))
    app_pool.add("mn_conv11_dw", AppConfig(prr_shape=(1, 2), glb=4,  runtime=26))
    app_pool.add("mn_conv11_pw2", AppConfig(prr_shape=(1, 6), glb=8,  runtime=61))
    app_pool.add("mn_conv11_pw2", AppConfig(prr_shape=(1, 2), glb=2,  runtime=183))

    app_pool.add("mn_conv12_pw", AppConfig(prr_shape=(1, 6), glb=8,  runtime=98))
    app_pool.add("mn_conv12_pw", AppConfig(prr_shape=(1, 2), glb=2,  runtime=294))
    app_pool.add("mn_conv12_dw", AppConfig(prr_shape=(1, 2), glb=4,  runtime=39))
    app_pool.add("mn_conv12_pw2", AppConfig(prr_shape=(1, 6), glb=8,  runtime=98))
    app_pool.add("mn_conv12_pw2", AppConfig(prr_shape=(1, 2), glb=2,  runtime=294))

    app_pool.add("mn_conv13_pw", AppConfig(prr_shape=(1, 6), glb=8,  runtime=98))
    app_pool.add("mn_conv13_pw", AppConfig(prr_shape=(1, 2), glb=2,  runtime=294))
    app_pool.add("mn_conv13_dw", AppConfig(prr_shape=(1, 2), glb=4,  runtime=39))
    app_pool.add("mn_conv13_pw2", AppConfig(prr_shape=(1, 6), glb=8,  runtime=98))
    app_pool.add("mn_conv13_pw2", AppConfig(prr_shape=(1, 2), glb=2,  runtime=294))

    app_pool.add("mn_conv14_pw", AppConfig(prr_shape=(1, 6), glb=8,  runtime=98))
    app_pool.add("mn_conv14_pw", AppConfig(prr_shape=(1, 2), glb=2,  runtime=294))
    app_pool.add("mn_conv14_dw", AppConfig(prr_shape=(1, 2), glb=4,  runtime=21))
    app_pool.add("mn_conv14_pw2", AppConfig(prr_shape=(1, 6), glb=8,  runtime=45))
    app_pool.add("mn_conv14_pw2", AppConfig(prr_shape=(1, 2), glb=2,  runtime=135))

    app_pool.add("mn_conv15_pw", AppConfig(prr_shape=(1, 6), glb=8,  runtime=75))
    app_pool.add("mn_conv15_pw", AppConfig(prr_shape=(1, 2), glb=2,  runtime=225))
    app_pool.add("mn_conv15_dw", AppConfig(prr_shape=(1, 2), glb=4,  runtime=49))
    app_pool.add("mn_conv15_pw2", AppConfig(prr_shape=(1, 6), glb=8,  runtime=75))
    app_pool.add("mn_conv15_pw2", AppConfig(prr_shape=(1, 2), glb=2,  runtime=225))

    app_pool.add("mn_conv16_pw", AppConfig(prr_shape=(1, 6), glb=8,  runtime=75))
    app_pool.add("mn_conv16_pw", AppConfig(prr_shape=(1, 2), glb=2,  runtime=225))
    app_pool.add("mn_conv16_dw", AppConfig(prr_shape=(1, 2), glb=4,  runtime=49))
    app_pool.add("mn_conv16_pw2", AppConfig(prr_shape=(1, 6), glb=8,  runtime=75))
    app_pool.add("mn_conv16_pw2", AppConfig(prr_shape=(1, 2), glb=2,  runtime=225))

    app_pool.add("mn_conv17_pw", AppConfig(prr_shape=(1, 6), glb=8,  runtime=75))
    app_pool.add("mn_conv17_pw", AppConfig(prr_shape=(1, 2), glb=2,  runtime=225))
    app_pool.add("mn_conv17_dw", AppConfig(prr_shape=(1, 2), glb=4,  runtime=49))
    app_pool.add("mn_conv17_pw2", AppConfig(prr_shape=(1, 6), glb=8,  runtime=150))
    app_pool.add("mn_conv17_pw2", AppConfig(prr_shape=(1, 2), glb=2,  runtime=450))



    app_pool.add("cp", AppConfig(prr_shape=(1, 2), glb=3, runtime=2074))
    # app_pool.add("cp", AppConfig(prr_shape=(1, 6), glb=12, runtime=518))

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

    lapidary = Lapidary(accelerator_config=args.arch, workload_config=args.workload, app_pool=app_pool)
    lapidary.run()
    if args.log:
        workload_name = os.path.basename(args.workload).rsplit('.', 1)[0]
        log_dir = os.path.join("logs", workload_name)
        lapidary.dump_logs(log_dir)
