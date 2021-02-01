# ! /usr/bin/env python3
"""
Author: JanuxHsu
"""

import json
import logging
import os
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

from core_utils import API_Handler, setup_default_logger, read_json_from_file

parser = ArgumentParser()
parser.add_argument("-c", "--cluster", required=True, help="Target Cluster", dest="cluster")
parser.add_argument("-f", "--config", required=True, help="User/Password config", dest="config")
parser.add_argument("-o", "--api_port", required=False, help="API Port", default=443, dest="port")
parser.add_argument("-i", "--input_volumes", required=True, help="Target Volumes", dest="input_vols")
args = parser.parse_args()

setup_default_logger()

main_logger = logging.getLogger(os.path.basename(__file__))


def human_readable_size(size=None, units=None):
    """ Returns a human readable string representation of bytes """
    if units is None:
        units = [' bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
    return str(size) + units[0] if size < 1024 else human_readable_size(size >> 10, units[1:])


def save_results_to_file(output_filename="temp", data=None):
    with open('{}.json'.format(output_filename), 'w', encoding='utf-8') as output_file:
        json.dump(data, output_file, ensure_ascii=False, indent=4)

    main_logger.info("Write volumes data into [{}] - completed.".format(output_filename))


if __name__ == "__main__":
    try:
        config_file = Path(args.config)
        if not config_file.is_file():
            raise Exception("Cannot find connection config file. ({})".format(config_file))

        input_vol_file = Path(args.input_vols)
        if not input_vol_file.is_file():
            raise Exception("{} cannot be found, check file path or use volume_finder.py to create new one.".format(args.input_vols))

        config_json = read_json_from_file(file_path=config_file)

        main_logger.info("Start fetch all volumes in {}.".format(args.cluster))

        api_handler = API_Handler()
        api_handler.set_cluster(cluster=args.cluster)

        api_handler.set_api_user(api_user=config_json["account"])
        api_handler.set_api_password(api_password=config_json["password"])
        api_handler.set_port(port=args.port)

        records = []

        volumes = read_json_from_file(file_path=args.input_vols)

        main_logger.info("Found {} Volumes from {}.".format(len(volumes), args.input_vols))

        for record in volumes:
            volume_uuid = record["uuid"]
            volume_name = record["name"]

            snapshot_name = "auto_backup_{}".format(datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S"))
            main_logger.info("Create snapshot for {}.".format(volume_name))
            snapshot_create_res = api_handler.create_snapshot(volume_uuid=volume_uuid, snapshot_name=snapshot_name)
            main_logger.info("Create snapshot for {}. - Completed. Job uuid: {}".format(volume_name, snapshot_create_res["job"]["uuid"]))

        main_logger.info("Program ended.")

    except Exception as error:
        main_logger.exception(error)
