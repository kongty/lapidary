import argparse
from lapidary.lapidary import Lapidary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CGRA simulation")
    parser.add_argument("--arch", metavar="arch file", type=str,
                        default="./cfg/hw/amber.yml", help="Path to the architecture config file")
    parser.add_argument("--workload", metavar="workload file", type=str,
                        default="./cfg/workload/workload_0.yml", help="Path to the workload config file")
    parser.add_argument("--log-dir", metavar="log dir", type=str, default="./logs", help="Path to log directory")
    args = parser.parse_args()

    lapidary = Lapidary(architecture_filename=args.arch, workload_filename=args.workload)
    lapidary.run(until=300)
