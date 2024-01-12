import os
import time

from core.flow_chart import FlowChart
from modules.webhook_api import webhook_send

if __name__ == '__main__':
    while True:
        target_ip = input('输入目标IP:\n')
        target_desc = input('输入目标型号:\n')
        params = {'rsas': {}}
        params['rsas']['target_ip'] = target_ip
        params['rsas']['target_desc'] = '{}_{}'.format(
            target_desc, time.strftime('%m%d%M%S', time.localtime(time.time()))
        )
        fc = FlowChart(prerequisite=params)
        fc.load_map(hook_script='rsas_scan.py', map_json='绿盟扫描测试.pos')
        end = False
        while not end:
            end = fc.run_step()
        fc.params_bus['webhook'] = {
            'webhook_url': 'https://open.feishu.cn/open-apis/bot/v2/hook/49487983-e106-49c8-a527-4b8a4dfeddf5',
            'send_string': '绿盟扫描已完成'
        }
        fc.params_bus = webhook_send(params=fc.params_bus)
        os.abort()
