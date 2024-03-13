# sjl@smb.cn Aa123456789
import os

from modules.http_api import http_post, http_get

report_download_path = 'reports'
awvs_apikey = '1986ad8c0a5b3df4d7028d5f3c06e936c6d2855cc1d984e72bef3d7de3a3b61ec'
awvs_ip = '10.51.132.50'
awvs_port = '3443'


class Acunetix:
    def __init__(self, serve, api_key):
        self.api_key = api_key
        self.serve = serve
        self.headers = {'X-Auth': self.api_key,
                        'Content-type': 'application/json; charset=utf8'}

    def add_target(self, address, description, criticality=10):
        url = self.serve + '/api/v1/targets'
        body = {
            'address': address,
            'description': description,
            'criticality': criticality
        }
        params = {'http': {}}
        params['http']['url'] = url
        params['http']['data'] = body
        params['http']['headers'] = self.headers
        params = http_post(params=params)
        result = params['http']['response']
        return result

    def add_scan(self, target_id):
        url = self.serve + '/api/v1/scans'
        body = {
            "profile_id": "11111111-1111-1111-1111-111111111111",
            "incremental": False,
            "schedule": {"disable": False, "start_date": None, "time_sensitive": False},
            "report_template_id": "11111111-1111-1111-1111-111111111111",
            "target_id": target_id
        }
        params = {'http': {}}
        params['http']['url'] = url
        params['http']['data'] = body
        params['http']['headers'] = self.headers
        params = http_post(params=params)
        result = params['http']['response']
        return result

    def get_scan_id(self, target_id):
        url = self.serve + \
            '/api/v1/scans?l=20&q=target_id:{}'.format(target_id)
        params = {'http': {}}
        params['http']['url'] = url
        params['http']['headers'] = self.headers
        params = http_get(params=params)
        result = params['http']['response']
        result = result['scans'][0]['scan_id']
        return result

    def get_scan_status(self, target_id):
        url = self.serve + \
            '/api/v1/scans?l=20&q=target_id:{}'.format(target_id)
        params = {'http': {}}
        params['http']['url'] = url
        params['http']['headers'] = self.headers
        params = http_get(params=params)
        result = params['http']['response']
        result = result['scans'][0]['current_session']['status']
        return result

    def generate_report(self, target_id):
        scan_id = self.get_scan_id(target_id=target_id)
        url = self.serve + '/api/v1/reports'
        body = {
            "template_id": "11111111-1111-1111-1111-111111111115",
            "source": {
                "list_type": "scan_result",
                "id_list": ["{}".format(scan_id)]
            }
        }
        params = {'http': {}}
        params['http']['url'] = url
        params['http']['data'] = body
        params['http']['headers'] = self.headers
        params = http_get(params=params)
        result = params['http']['response']
        result = result['reports'][0]['report_id']
        return result

    def get_report_status(self, description):
        url = self.serve + '/api/v1/reports?l=20&s=template:desc'
        params = {'http': {}}
        params['http']['url'] = url
        params['http']['headers'] = self.headers
        params = http_get(params=params)
        result = params['http']['response']
        result = result['reports']
        for i in result:
            if description in i['source']['description']:
                return i['status']

    def download_report(self, description):
        url = self.serve + '/api/v1/reports?l=20&s=template:desc'
        params = {'http': {}}
        params['http']['url'] = url
        params['http']['headers'] = self.headers
        params = http_get(params=params)
        result = params['http']['response']
        result = result['reports']
        download_path = None
        for i in result:
            if description in i['source']['description']:
                download_path = i['download'][0]
        if download_path is not None:
            if description not in os.listdir(report_download_path):
                os.makedirs(r'{}\{}'.format(report_download_path, description))
            url = self.serve + download_path
            params = {'http': {}}
            params['http']['url'] = url
            params['http']['headers'] = self.headers
            params['http']['download_as'] = r"{}\{}\{}-WVS.html".format(
                report_download_path, description, description)
            http_get(params=params)
            return True
        else:
            return False


def awvs_start(params):
    params['awvs']['awvs_obj'] = Acunetix(
        serve='https://{}:{}'.format(awvs_ip, awvs_port), api_key=awvs_apikey)
    return params


def awvs_add_target(params):
    awvs_obj: Acunetix = params['awvs']['awvs_obj']
    target_ip = params['awvs']['target_ip']
    target_desc = params['awvs']['target_desc']
    target_id = awvs_obj.add_target(
        address=target_ip, description=target_desc)['target_id']
    params['awvs']['target_id'] = target_id
    return params


def awvs_add_scan(params):
    awvs_obj: Acunetix = params['awvs']['awvs_obj']
    target_id = params['awvs']['target_id']
    awvs_obj.add_scan(target_id=target_id)
    return params


def awvs_get_scan_status(params):
    awvs_obj: Acunetix = params['awvs']['awvs_obj']
    target_id = params['awvs']['target_id']
    scan_status = awvs_obj.get_scan_status(target_id=target_id)
    params['awvs']['scan_status'] = scan_status
    return params


def awvs_generate_report(params):
    awvs_obj: Acunetix = params['awvs']['awvs_obj']
    target_id = params['awvs']['target_id']
    awvs_obj.generate_report(target_id=target_id)
    return params


def awvs_get_report_status(params):
    awvs_obj: Acunetix = params['awvs']['awvs_obj']
    target_desc = params['awvs']['target_desc']
    report_status = awvs_obj.get_report_status(description=target_desc)
    params['awvs']['report_status'] = report_status
    return params


def awvs_download_report(params):
    awvs_obj: Acunetix = params['awvs']['awvs_obj']
    target_desc = params['awvs']['target_desc']
    awvs_obj.download_report(description=target_desc)
    return params
