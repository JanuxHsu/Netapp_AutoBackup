# ! /usr/bin/env python3
"""
Author: JanuxHsu
"""

import base64
import json
import logging

import requests
import urllib3

urllib3.disable_warnings()


def setup_default_logger(log_level=logging.INFO):
    logging.basicConfig(level=log_level,
                        format='%(levelname)-8s[%(asctime)s] %(name)-14s:  %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    console = logging.StreamHandler()
    console.setLevel(log_level)


class API_Handler(object):
    def __init__(self):
        self.port = 443
        self.auth_header = None
        self.cluster = ""
        self.api_user = ""
        self.api_password = ""
        self.logger = logging.getLogger(self.__class__.__name__)

    def set_cluster(self, cluster=""):
        self.cluster = cluster

    def set_api_user(self, api_user=""):
        self.api_user = api_user

    def set_api_password(self, api_password=""):
        self.api_password = api_password

    def set_port(self, port=443):
        self.port = port

    def _get_url(self):
        return "https://{}:{}".format(self.cluster, self.port)

    def generate_auth_header(self):
        base64string = base64.encodebytes(('%s:%s' % (self.api_user, self.api_password)).encode()).decode().replace(
            '\n', '')

        headers = {
            'authorization': "Basic %s" % base64string,
            'content-type': "application/json",
            'accept': "application/json"
        }

        self.auth_header = headers
        return headers

    def list_volumes(self, fields=None, included_root_vols=False):
        self.generate_auth_header()

        queries = []
        if not included_root_vols:
            queries.append("is_svm_root=false")
        if fields is not None:
            queries.append("fields={}".format(",".join(fields)))

        url = "{}/api/storage/volumes{}".format(self._get_url(), "?{}".format("&".join(queries)))
        response = requests.get(url, headers=self.auth_header, verify=False, timeout=30)
        res_json = response.json()

        if not response.ok:
            raise Exception(res_json)
        return res_json["records"]

    def show_volume(self, uuid=None, fields=None):
        self.generate_auth_header()

        query = "" if fields is None else "?fields={}".format(",".join(fields))

        url = "{}/api/storage/volumes/{}{}".format(self._get_url(), uuid, query)
        response = requests.get(url, headers=self.auth_header, verify=False, timeout=30)
        res_json = response.json()

        if not response.ok:
            raise Exception(res_json)
        return res_json

    def create_snapshot(self, volume_uuid=None, snapshot_name=None):
        self.generate_auth_header()

        body = {"name": snapshot_name}

        url = "{}/api/storage/volumes/{}/snapshots".format(self._get_url(), volume_uuid)
        response = requests.post(url, headers=self.auth_header, data=json.dumps(body), verify=False, timeout=30)
        res_json = response.json()

        if not response.ok:
            raise Exception(res_json)
        return res_json

    def show_snapshot(self, volume_uuid=None, snapshot_uuid=None):
        self.generate_auth_header()
        url = "{}/api/storage/volumes/{}/snapshots/{}".format(self._get_url(), volume_uuid, snapshot_uuid)
        response = requests.get(url, headers=self.auth_header, verify=False, timeout=30)
        res_json = response.json()

        if not response.ok:
            raise Exception(res_json)
        return res_json

    def list_snapshots(self, volume_uuid=None, target=None):
        self.generate_auth_header()

        query = "" if target is None else "?name={}".format(",".join(target))

        url = "{}/api/storage/volumes/{}/snapshots{}".format(self._get_url(), volume_uuid, query)
        response = requests.get(url, headers=self.auth_header, verify=False, timeout=30)
        res_json = response.json()

        if not response.ok:
            raise Exception(res_json)
        return res_json

    def get_volume_uuid_by_name(self, name=""):
        self.generate_auth_header()

        url = "{}/api/storage/volumes?name={}".format(self._get_url(), name)
        response = requests.get(url, headers=self.auth_header, verify=False, timeout=30)
        res_json = response.json()

        if not response.ok:
            raise Exception(res_json)
        elif res_json["num_records"] != 1:
            raise Exception("Found no match volumes using [{}], please check input again.".format(name))

        volume_info = res_json["records"][0]

        return volume_info["uuid"], volume_info["name"]

    def get_job_by_uuid(self, uuid=None):
        if uuid is None:
            raise Exception("uuid must be given,")

        self.generate_auth_header()

        url = "{}/api/cluster/jobs/{}".format(self._get_url(), uuid)
        response = requests.get(url, headers=self.auth_header, verify=False, timeout=30)
        res_json = response.json()
        if not response.ok:
            raise Exception(res_json)
        return res_json


def read_json_from_file(file_path=None):
    with open(file_path) as f:
        config = json.load(f)
        return config

