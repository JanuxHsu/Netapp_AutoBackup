import base64
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
        self.generate_auth_header()

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
        base64string = base64.encodebytes(('%s:%s' % (self.api_user, self.api_password)).encode()).decode().replace('\n', '')

        headers = {
            'authorization': "Basic %s" % base64string,
            'content-type': "application/json",
            'accept': "application/json"
        }

        self.auth_header = headers
        return headers

    def check_snapmirror_by_id(self, uuid=""):
        snap_api_url = "{}/api/snapmirror/relationships/{}".format(self._get_url(), uuid)

        response = requests.get(snap_api_url, headers=self.auth_header, verify=False)

        res_json = response.json()

        if response.status_code != 200:
            raise Exception(res_json)

        return res_json
