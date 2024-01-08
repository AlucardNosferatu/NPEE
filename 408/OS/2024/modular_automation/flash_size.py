import os
import time

from core.flow_chart import FlowChart
from modules.webhook_api import webhook_send

if __name__ == '__main__':
    params = {
        'console': {  # SSH连WAN口模式
            'console_type': 'ssh',
            'dut_ip': '192.168.110.1',
            'ssh_pass': '2d9e7c0333cd4f5d'
        }
    }
    fc = FlowChart(prerequisite=params)
    fc.load_map(hook_script='flash_size.py', map_json='查询Flash容量.pos')
    end = False
    while not end:
        end = fc.run_step()
    os.abort()
