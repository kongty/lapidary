import argparse
from lapidary.lapidary import Lapidary

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CGRA simulation')
    parser.add_argument('--config', metavar='config file', type=str,
                        default="./cfg/hw/amber.cfg", help="Path to the config file")
    parser.add_argument('--log-dir', metavar='log dir', type=str,
                        default="./logs", help="Path to log directory")

    args = parser.parse_args()
    lapidary = Lapidary(args.config)
    lapidary.run()
