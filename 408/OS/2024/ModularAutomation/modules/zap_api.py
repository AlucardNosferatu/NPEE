import os
import time

from zapv2 import ZAPv2

from modules.http_api import http_get
from modules.misc import process_kill

report_download_path = 'reports'
jar_filename = 'zap-2.12.0.jar'


def zap_kill_java(params):
    params['misc'] = {'kill_processes': ['javaw.exe', 'java.exe']}
    params = process_kill(params=params)
    return params


def zap_start_exe(params):
    zap_params = params['zap']
    exe_dir = zap_params['exe_dir']
    disk = exe_dir[:2]
    # os.system('{} && cd "{}" && ZAP.exe'.format(disk, exe_dir))
    os.popen('{} && cd "{}" && java -jar {}'.format(disk, exe_dir, jar_filename))
    print('开始启动ZAP')
    time.sleep(45)
    return params


def zap_init_adapter(params):
    zap_params = params['zap']
    api_key = zap_params['api_key']
    proxy_port = zap_params['proxy_port']
    adapter_obj = ZAPv2(
        apikey=api_key,
        proxies={'http': 'http://127.0.0.1:{}'.format(
            proxy_port), 'https': 'http://127.0.0.1:{}'.format(proxy_port)}
    )
    zap_params['adapter_obj'] = adapter_obj
    return params


def zap_crawl_target(params):
    adapter_obj: ZAPv2 = params['zap']['adapter_obj']
    target_url = params['zap']['target_url']
    crawl_id = adapter_obj.spider.scan(url=target_url)
    params['zap']['crawl_id'] = crawl_id
    return params


def zap_get_crawl_status(params):
    adapter_obj: ZAPv2 = params['zap']['adapter_obj']
    crawl_id = params['zap']['crawl_id']
    crawl_status = adapter_obj.spider.status(scanid=crawl_id)
    params['zap']['crawl_status'] = crawl_status
    return params


def zap_scan_target(params):
    adapter_obj: ZAPv2 = params['zap']['adapter_obj']
    target_url = params['zap']['target_url']
    scan_id = adapter_obj.ascan.scan(url=target_url)
    params['zap']['scan_id'] = scan_id
    return params


def zap_get_scan_status(params):
    adapter_obj: ZAPv2 = params['zap']['adapter_obj']
    scan_id = params['zap']['scan_id']
    scan_status = adapter_obj.ascan.status(scanid=scan_id)
    params['zap']['scan_status'] = scan_status
    return params


def zap_download_report(params):
    zap_params = params['zap']
    proxy_port = zap_params['proxy_port']
    api_key = zap_params['api_key']
    headers = {
        'Accept': 'application/json',
        'X-ZAP-API-Key': api_key
    }
    url = 'http://localhost:{}/OTHER/core/other/htmlreport/'.format(proxy_port)

    params = {'http': {}}
    params['http']['url'] = url
    params['http']['headers'] = headers
    params['http']['raw'] = True
    params = http_get(params=params)
    result = params['http']['response']

    target_desc = zap_params['target_desc']
    if target_desc not in os.listdir(report_download_path):
        os.makedirs(r"{}\{}".format(report_download_path, target_desc))
    with open(r"{}\{}\{}-ZAP.html".format(report_download_path, target_desc, target_desc), "w", encoding='utf-8') as f:
        f.write(result.text)
    return params
