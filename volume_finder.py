import logging
import os
from argparse import ArgumentParser
from pathlib import Path

from core_utils import API_Handler, setup_default_logger

parser = ArgumentParser()
parser.add_argument("-c", "--cluster", required=True, help="Target Cluster", dest="cluster")
parser.add_argument("-f", "--config", required=True, help="User/Password config", dest="config")
parser.add_argument("-o", "--api_port", required=False, help="API Port", default=443, dest="port")
args = parser.parse_args()

setup_default_logger()

main_logger = logging.getLogger(os.path.basename(__file__))

if __name__ == "__main__":
    config_file = Path(args.config)
    if not config_file.is_file():
        raise Exception("Cannot find connection config file. ({})".format(config_file))

    api_handler = API_Handler()
    api_handler.set_cluster(cluster=args.cluster)
