import json
import os
import re
import time
import zipfile

from modules.http_api import http_get, http_post

report_download_path = 'reports'
lm_ip = '10.48.24.59'


class NSFocusRSAS:
    def __init__(self, serve='https://{}'.format(lm_ip)):
        self.serve = serve
        self.token = self.get_token()

    def get_headers(self):
        headers = {
            'Cache-Control': 'max-age=0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.77 Safari/537.36',
            'Cookie': 'csrftoken={}; left_menustatue_NSFOCUSRSAS=0|0|https://{}/task/task_entry/; sessionid={}'.format(
                self.token['csrftoken'], lm_ip, self.token['sessionid']
            ), 'Referer': 'https://{}/task/task_entry/'.format(lm_ip)
        }
        return headers

    def get_token(self):
        # noinspection SpellCheckingInspection
        headers = {
            'Cache-Control': 'max-age=0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.77 Safari/537.36',
            'Cookie': 'csrftoken=a0GBEJkHZHkRHkeKL45tUwhvyCZlFhSJnh9Nod9y2GN4mwTa4zAFCVtAsCWFqS5x; '
                      'left_menustatue_NSFOCUSRSAS=0|0|https://{}/task/task_entry/; '
                      'sessionid=c31bpn3c4yohycuilnzlt6gtmlibvn0t'.format(lm_ip),
            'Referer': 'https://{}/'.format(lm_ip)
        }
        url = self.serve + '/accounts/login_view/'

        params = {'http': {}}
        params['http']['url'] = url
        params['http']['headers'] = headers
        params['http']['raw'] = True
        params = http_get(params=params)
        result = params['http']['response']

        print(result.headers)
        csrfmiddlewaretoken = re.findall('name=\'csrfmiddlewaretoken\' value="(.*?)"', result.text)[0]

        body = {
            'username': 'smb', 'password': 'U2FsdGVkX1+f1WRj0T3xezMHmqY/K3ypJM+lV9t1Fzc=',
            'csrfmiddlewaretoken': csrfmiddlewaretoken
        }
        url = self.serve + '/accounts/login_view/'

        params = {'http': {}}
        params['http']['url'] = url
        params['http']['data'] = body
        params['http']['data_format'] = 'url_encoded'
        params['http']['headers'] = headers
        params['http']['allow_redirects'] = False
        params['http']['raw'] = True
        params = http_post(params=params)
        result = params['http']['response']

        csrftoken = re.findall('csrftoken=(.*?);', str(result.headers))[0]
        sessionid = re.findall('sessionid=(.*?);', str(result.headers))[0]
        return {'csrftoken': csrftoken, 'sessionid': sessionid}

    def add_target(self, address, name):
        headers = self.get_headers()
        url = self.serve + '/task/index/1?entry_template_id=12'

        params = {'http': {}}
        params['http']['url'] = url
        params['http']['headers'] = headers
        params['http']['raw'] = True
        params = http_get(params=params)
        result = params['http']['response']

        csrfmiddlewaretoken = re.findall("\"csrfmiddlewaretoken\":'(.*?)'", result.text)[0]
        print(csrfmiddlewaretoken)

        body = {
            "csrfmiddlewaretoken": csrfmiddlewaretoken, "vul_or_pwd": "vul", "config_task": "taskname",
            "task_config": "", "diff": "write something", "target": "ip", "ipList": address, "domainList": "",
            "name": name, "exec": "immediate", "exec_timing_date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "exec_everyday_time": "00:00", "exec_everyweek_day": "1", "exec_everyweek_time": "00:00",
            "exec_emonthdate_day": "1", "exec_emonthdate_time": "00:00", "exec_emonthweek_pre": "1",
            "exec_emonthweek_day": "1", "exec_emonthweek_time": "00:00", "tpl": "12", "login_ifuse": "yes",
            "login_check_type": "login_check_type_vul", "batch_ssh_ip": "", "batch_ssh_protocol": "SSH",
            "batch_ssh_port": "", "batch_ssh_name": "", "isguesspwd": "yes", "exec_range": "", "scan_pri": "2",
            "taskdesc": "", "report_type_html": "html", "report_content_sum": "sum", "report_content_host": "host",
            "report_tpl_sum": "1", "report_tpl_host": "101", "report_ifsent_type": "html", "report_ifsent_email": "",
            "port_strategy": "standard", "port_strategy_userports": "1-100,443,445", "port_speed": "3", "port_tcp": "T",
            "live": "on", "live_icmp": "on", "live_udp_ports": "25,53", "live_tcp": "on",
            "live_tcp_ports": "21,22,23,25,80,443,445,139,3389,6000", "sping_delay": "1", "scan_level": "3",
            "timeout_plugins": "40", "timeout_read": "5", "alert_msg": "zdh-test", "scan_oracle": "yes",
            "encoding": "GBK", "bvs_task": "no", "pwd_smb": "yes", "pwd_type_smb": "c",
            "pwd_user_smb": "smb_user.default", "pwd_pass_smb": "smb_pass.default", "pwd_telnet": "yes",
            "pwd_type_telnet": "c", "pwd_user_telnet": "telnet_user.default", "pwd_pass_telnet": "telnet_pass.default",
            "pwd_ssh": "yes", "pwd_type_ssh": "c", "pwd_user_ssh": "ssh_user.default",
            "pwd_pass_ssh": "ssh_pass.default", "pwd_timeout": "5", "pwd_timeout_time": "120", "pwd_interval": "0",
            "pwd_num": "0",
            'loginarray': '[{"ip_range": "' + address + '", "admin_id": "", "protocol": "", "port": "", "os": "", '
                                                        '"ssh_auth": "", "user_name": "", "user_pwd": "", '
                                                        '"user_ssh_key": "", "ostpls": [], "apptpls": [], '
                                                        '"dbtpls": [], "virttpls": [], "bdstpls": [], "devtpls": '
                                                        '[], "statustpls": "", "tpl_industry": "", "tpllist": [], '
                                                        '"tpllistlen": 0, "web_login_url": "", '
                                                        '"web_login_cookie": "", "jhosts": [], "tpltype": "", '
                                                        '"protect": "", "protect_level": "", "jump_ifuse": "", '
                                                        '"host_ifsave": "", "oracle_ifuse": "", "ora_username": '
                                                        '"", "ora_userpwd": "", "ora_port": "", "ora_usersid": '
                                                        '"", "weblogic_ifuse": "", "weblogic_system": "", '
                                                        '"weblogic_version": "", "weblogic_user": "", '
                                                        '"weblogic_path": "", "web_login_wblgc_ifuse": "", '
                                                        '"web_login_wblgc_user": "", "web_login_wblgc_pwd": "", '
                                                        '"web_login_wblgc_path": ""}]'
        }
        url = self.serve + '/task/vul/tasksubmit'

        params = {'http': {}}
        params['http']['url'] = url
        params['http']['data'] = body
        params['http']['data_format'] = 'url_encoded'
        params['http']['headers'] = headers
        params['http']['raw'] = True
        params = http_post(params=params)
        result = params['http']['response']

        print(result.text)

    def get_scan_status(self, name):
        headers = self.get_headers()
        url = self.serve + '/list/'

        params = {'http': {}}
        params['http']['url'] = url
        params['http']['headers'] = headers
        params['http']['timeout'] = 3600
        params['http']['raw'] = True
        params = http_get(params=params)
        result = params['http']['response']

        csrf_middleware_token = re.findall("csrfmiddlewaretoken:'(.*?)'", result.text)[0]

        url = self.serve + '/list/getList'
        body = {
            'csrfmiddlewaretoken': csrf_middleware_token, 'ip': '', 'task_name': name, 'domain': '', 'task_status': '',
            'rs_template': '', 'account': '', 'time_start_scan': '', 'time_end_scan': '', 'task_type': '', 'page': '1',
            'page_count': '25'
        }

        params = {'http': {}}
        params['http']['url'] = url
        params['http']['data'] = body
        params['http']['data_format'] = 'url_encoded'
        params['http']['headers'] = headers
        params['http']['timeout'] = 120
        params['http']['raw'] = True
        params = http_post(params=params)
        result = params['http']['response']

        end_time = re.findall("id='endtime(.*?)<", result.text)[0]
        print(end_time)
        if '-' in end_time and ':' in end_time:
            return 'over'
        else:
            return 'starting'

    def generate_report(self, name):
        headers = self.get_headers()
        url = self.serve + '/report/tasklist/type/7/offset/50?nocache='

        params = {'http': {}}
        params['http']['url'] = url
        params['http']['headers'] = headers
        params['http']['raw'] = True
        params = http_get(params=params)
        result = params['http']['response']

        report_id = None
        for i in json.loads(result.text):
            if name in i['text']:
                report_id = i['id']
        print(report_id)

        url = self.serve + '/report/'

        params = {'http': {}}
        params['http']['url'] = url
        params['http']['headers'] = headers
        params['http']['raw'] = True
        params = http_get(params=params)
        result = params['http']['response']

        print(result.text)
        csrfmiddlewaretoken = re.findall("csrfmiddlewaretoken': '(.*?)'", result.text)[0]

        url = self.serve + '/report/export'
        body = {
            "export_area": "sys", "report_type": "pdf", "report_content": "summary", "summary_template_id": "1",
            "summary_report_title": "zdh-test", "host_template_id": "101", "single_report_title": "zdh-test",
            "multi_export_type": "multi_sum", "multi_report_name": "zdh-test", "single_task_report_name": "",
            "csrfmiddlewaretoken": csrfmiddlewaretoken, "from": "report_export", 'task_id': report_id
        }

        params = {'http': {}}
        params['http']['url'] = url
        params['http']['data'] = body
        params['http']['data_format'] = 'url_encoded'
        params['http']['headers'] = headers
        params['http']['raw'] = True
        params = http_post(params=params)
        result = params['http']['response']

        print(result)
        report_id_id = re.findall('"report_id": (.*?)}', result.text)[0]
        return report_id_id

    def get_report_status(self, name):
        headers = self.get_headers()
        url = self.serve + '/report/list'

        params = {'http': {}}
        params['http']['url'] = url
        params['http']['headers'] = headers
        params['http']['raw'] = True
        params = http_get(params=params)
        result = params['http']['response']

        csrfmiddlewaretoken = re.findall('csrfmiddlewaretoken\' value="(.*?)"', result.text)[0]

        body = {
            'report_name': name, 'start_time': '', 'end_time': '', 'csrfmiddlewaretoken': csrfmiddlewaretoken,
            'page_size': '25', 'report_content': '', 'data_area': '0'
        }
        url = self.serve + '/report/list/get_report_list/page/1'

        params = {'http': {}}
        params['http']['url'] = url
        params['http']['data'] = body
        params['http']['data_format'] = 'url_encoded'
        params['http']['headers'] = headers
        params['http']['raw'] = True
        params = http_post(params=params)
        result = params['http']['response']

        status = re.findall('/media/stylesheet/nsfocus_2012/images/blank.gif" width="(.*?)"', result.text)[0]
        if '100' in status:
            status = 'over'
        else:
            status = 'starting'
        return status

    def download_report(self, name, report_id, file_path='', folder_abs=''):
        headers = self.get_headers()
        url = self.serve + '/report/download/id/{}/type/pdf/'.format(report_id)

        params = {'http': {}}
        params['http']['url'] = url
        params['http']['headers'] = headers
        params['http']['raw'] = True
        params = http_get(params=params)
        result = params['http']['response']

        if name not in os.listdir(report_download_path):
            os.makedirs(r"{}\{}".format(report_download_path, name))
        with open(file_path, 'wb') as f:
            f.write(result.content)
            f.close()
        print('保存成功 {}'.format(file_path))
        # todo: add archive files handler
        zip_file = zipfile.ZipFile(file_path)
        zip_list = zip_file.namelist()  # 得到压缩包里所有文件
        for f in zip_list:
            if 'index' in str(f):
                zip_file.extract(f, folder_abs)  # 循环解压文件到指定目录
        zip_file.close()  # 关闭文件，必须有，释放内存
        print('解压成功 {}'.format(file_path))
        time.sleep(5)
        os.remove(file_path)
        list_dir = os.listdir(r"{}\{}".format(report_download_path, name))
        for i in list_dir:
            if 'index' in i:
                src_file = r"{}\{}\index.pdf".format(report_download_path, name)
                dst_file = r"{}\{}\{}-绿盟.pdf".format(report_download_path, name, name)
                os.rename(src_file, dst_file)


def rsas_start(params):
    params['rsas']['rsas_obj'] = NSFocusRSAS()
    return params


def rsas_scan_target(params):
    rsas_obj: NSFocusRSAS = params['rsas']['rsas_obj']
    target_ip = params['rsas']['target_ip']
    target_desc = params['rsas']['target_desc']
    finished = False
    while not finished:
        try:
            rsas_obj.add_target(address=target_ip, name=target_desc)
            finished = True
        except Exception as e:
            _ = e
    return params


def rsas_get_scan_status(params):
    rsas_obj: NSFocusRSAS = params['rsas']['rsas_obj']
    target_desc = params['rsas']['target_desc']
    finished = False
    while not finished:
        try:
            scan_status = rsas_obj.get_scan_status(name=target_desc)
            params['rsas']['scan_status'] = scan_status
            finished = True
        except Exception as e:
            _ = e
    return params


def rsas_generate_report(params):
    rsas_obj: NSFocusRSAS = params['rsas']['rsas_obj']
    target_desc = params['rsas']['target_desc']
    finished = False
    while not finished:
        try:
            report_id = rsas_obj.generate_report(name=target_desc)
            params['rsas']['report_id'] = report_id
            finished = True
        except Exception as e:
            _ = e
    return params


def rsas_get_report_status(params):
    rsas_obj: NSFocusRSAS = params['rsas']['rsas_obj']
    target_desc = params['rsas']['target_desc']
    finished = False
    while not finished:
        try:
            report_status = rsas_obj.get_report_status(name=target_desc)
            params['rsas']['report_status'] = report_status
            finished = True
        except Exception as e:
            _ = e
    return params


def rsas_download_report(params):
    rsas_obj: NSFocusRSAS = params['rsas']['rsas_obj']
    target_desc = params['rsas']['target_desc']
    report_id = params['rsas']['report_id']
    file_path = r"{}\{}\{}-RSAS.zip".format(report_download_path, target_desc, target_desc)
    folder_abs = r"{}\{}".format(report_download_path, target_desc)
    finished = False
    while not finished:
        try:
            rsas_obj.download_report(name=target_desc, report_id=report_id, file_path=file_path, folder_abs=folder_abs)
            finished = True
        except Exception as e:
            _ = e
    return params
