import os
import time

from core.flow_chart import FlowChart
from modules.webhook_api import webhook_send

if __name__ == '__main__':
    target_addr = 'http://10.51.132.240/'
    params = {
        'zap': {
            'exe_dir': r"C:\Program Files\OWASP\Zed Attack Proxy",
            'api_key': 'home',
            'proxy_port': '8081',
            'target_url': {True: target_addr, False: 'http://{}'.format(target_addr)}['http' in target_addr],
            'target_desc': 'EW1300G-ExtDDR_' + time.strftime('%m%d%M%S', time.localtime(time.time())),
            'target_eweb_pass': 'LostXmas20291224'
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
