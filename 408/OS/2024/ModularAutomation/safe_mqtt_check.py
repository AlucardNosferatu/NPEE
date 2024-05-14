from modules.logger import log_handler_init, log_logger_init
from modules.webhook_api import webhook_send
from core.flow_chart import FlowChart
import os
from safe_common_config import target_name, serial_number, scan_host

if __name__ == '__main__':
    params = {}
    params['debug'] = True
    params['mqtt'] = {
        'host': scan_host,
        'topic': 'sys/#'
    }
    params['sn'] = serial_number
    params['product'] = target_name
    params['save_txt'] = 'reports/{} MQTT加密测试.txt'.format(params['product'])
    fc = FlowChart(prerequisite=params)
    fc.load_map(hook_script='mqtt_check.py', map_json='MQTT加密测试.pos')
    # todo: makeshift patch
    fc.params_bus['log'] = {'logger_name': 'mqtt_check', 'log_backup_count': 8192}
    fc.params_bus = log_logger_init(params=fc.params_bus)
    fc.params_bus = log_handler_init(params=fc.params_bus)
    end = False
    while not end:
        end = fc.run_step()
    fc.params_bus['webhook'] = {
        'webhook_url': 'https://open.feishu.cn/open-apis/bot/v2/hook/49487983-e106-49c8-a527-4b8a4dfeddf5',
        'send_string': '{}的MQTT加密测试已完成'.format(target_name)
    }
    fc.params_bus = webhook_send(params=fc.params_bus)
    os.abort()
