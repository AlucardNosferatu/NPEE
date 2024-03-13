import os
import time

from core.flow_chart import FlowChart
from modules.webhook_api import webhook_send
from safe_common_config import scan_host_web, target_name
from safe_common_config import eweb_pass

if __name__ == '__main__':
    while True:
        target_ip = input('输入目标IP:\n')
        target_desc = input('输入目标型号:\n')
        target_pass = input('输入目标密码，默认为NO_PASSWORD，输入USE_CFG采用safe_common_config里的配置:\n')
        if target_ip == '':
            target_ip = scan_host_web
        if target_desc == '':
            target_desc = target_name
        if target_pass == '':
            target_pass = 'NO_PASSWORD'
        elif target_pass == 'USE_CFG':
            target_pass = eweb_pass
        zap_api_key = input('输入ZAP的API密钥，默认为arbfu3ifd1ckb6i1l33cq22ckj:\n')
        if zap_api_key == '':
            zap_api_key = 'arbfu3ifd1ckb6i1l33cq22ckj'
        zap_proxy_Port = input('输入ZAP本地代理端口，默认为8080:\n')
        if zap_proxy_Port == '':
            zap_proxy_Port = '8080'

        target_addr = 'https://{}/'.format(target_ip)
        params = {
            'zap': {
                'exe_dir': r"C:\Program Files\OWASP\Zed Attack Proxy",
                'api_key': zap_api_key,
                'proxy_port': '8080',
                'target_url': {True: target_ip, False: target_addr}['http' in target_ip],
                'target_desc': '{}_{}'.format(target_desc, time.strftime('%m%d%M%S', time.localtime(time.time()))),
                'target_eweb_pass': target_pass
            }
        }
        fc = FlowChart(prerequisite=params)
        fc.load_map(hook_script='zap_scan.py', map_json='ZAP页面扫描测试.pos')
        end = False
        while not end:
            end = fc.run_step()
        fc.params_bus['webhook'] = {
            'webhook_url': 'https://open.feishu.cn/open-apis/bot/v2/hook/49487983-e106-49c8-a527-4b8a4dfeddf5',
            'send_string': 'ZAP扫描已完成'
        }
        fc.params_bus = webhook_send(params=fc.params_bus)
        os.abort()
