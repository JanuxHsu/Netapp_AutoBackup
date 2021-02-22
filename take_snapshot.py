# ! /usr/bin/env python3
"""
Author: JanuxHsu
"""
from datetime import datetime, timedelta
import json
import logging
import os
from argparse import ArgumentParser
from pathlib import Path
from time import sleep

from core_utils import API_Handler, setup_default_logger, read_json_from_file

parser = ArgumentParser()
parser.add_argument("-c", "--cluster", required=True, help="Target Cluster", dest="cluster")
parser.add_argument("-f", "--config", required=True, help="User/Password config", dest="config")
parser.add_argument("-o", "--api_port", required=False, help="API Port", default=443, dest="port")
parser.add_argument("-n", "--volume_name", required=True, help="Volume Name", dest="name")
parser.add_argument("-l", "--log_level", required=False, default="INFO", choices=["INFO", "DEBUG"], dest="log_level")
args = parser.parse_args()

setup_default_logger()

main_logger = logging.getLogger(os.path.basename(__file__))

main_logger.setLevel(level=logging.INFO if args.log_level == "INFO" else logging.DEBUG)

if __name__ == "__main__":
    try:
        config_file = Path(args.config)
        if not config_file.is_file():
            raise Exception("Cannot find connection config file. ({})".format(config_file))

        config_json = read_json_from_file(file_path=config_file)

        api_handler = API_Handler()
        api_handler.set_cluster(cluster=args.cluster)

        api_handler.set_api_user(api_user=config_json["account"])
        api_handler.set_api_password(api_password=config_json["password"])
        api_handler.set_port(port=args.port)

        target_name = args.name

        volume_uuid, volume_name = api_handler.get_volume_uuid_by_name(name=target_name)

        snapshot_name = "snapshot.{}".format(datetime.utcnow().strftime("%Y%m%d_%H%M%S"))
        main_logger.info("Create snapshot {} for {}.".format(snapshot_name, volume_name))
        snapshot_create_res = api_handler.create_snapshot(volume_uuid=volume_uuid, snapshot_name=snapshot_name)

        job_uuid = snapshot_create_res["job"]["uuid"]
        main_logger.info("Create snapshot for {}. - Job created. Job uuid: {}".format(volume_name, job_uuid))

        job_res = {}
        main_logger.info("waiting for snapshot creation job to complete. (id: [{}])".format(job_uuid))
        # ======= start of while =========
        while job_res.get("end_time") is None:
            main_logger.debug("Checking job status...")
            job_res = api_handler.get_job_by_uuid(uuid=job_uuid)
            job_status = job_res["state"]
            main_logger.debug("job status: {}".format(job_status))
            if job_status == "success":
                break
            sleep(5)
        # ======= end of while =========
        main_logger.info("snapshot creation job completed. (id: [{}])".format(job_uuid))
        job_status = job_res["state"]

        if job_status == "success":
            start_time = job_res["start_time"]
            end_time = job_res["end_time"]
            start_datetime = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S%z")
            end_datetime = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S%z")

            duration = (end_datetime - start_datetime).seconds
            main_logger.info(
                "\nSnapshot [{}] successfully created for [{}].\nCreated at: {}.\nused {} seconds.".format(
                    snapshot_name,
                    volume_name,
                    end_time,
                    duration))
        else:
            job_message = job_res["message"]
            main_logger.error(
                "Error occurred when creating snapshot for {}.\nError:{}".format(volume_name, job_message))

    except Exception as error:
        main_logger.exception(error)
