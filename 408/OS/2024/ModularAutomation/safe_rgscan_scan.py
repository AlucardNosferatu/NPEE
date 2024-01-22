import os
import time

from core.flow_chart import FlowChart
from modules.webhook_api import webhook_send
from safe_common_config import scan_host, target_name

if __name__ == '__main__':
    params = {'rgscan': {}}
    login_token = input('请输入login token:')
    params['rgscan']['login_token'] = login_token
    params['rgscan']['target_ip'] = scan_host
    params['rgscan']['target_desc'] = '{}_{}'.format(target_name, time.strftime('%m%d%M%S', time.localtime(time.time())))
    fc = FlowChart(prerequisite=params)
    fc.load_map(hook_script='rgscan_scan.py', map_json='RGSCAN扫描测试.pos')
    end = False
    while not end:
        end = fc.run_step()
    fc.params_bus['webhook'] = {
        'webhook_url': 'https://open.feishu.cn/open-apis/bot/v2/hook/49487983-e106-49c8-a527-4b8a4dfeddf5',
        'send_string': 'RG-Scan扫描已完成'
    }
    fc.params_bus = webhook_send(params=fc.params_bus)
    os.abort()
