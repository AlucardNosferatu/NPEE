from modules.webhook_api import webhook_send
from core.flow_chart import FlowChart
import os
from safe_common_config import target_name, filename_bin, filename_rom, folder

if __name__ == '__main__':
    params = {'binwalk': {}}
    params['binwalk']['args'] = '-Me'
    params['binwalk']['target_file'] = filename_bin
    params['binwalk']['target_folder'] = folder
    params['binwalk']['save_txt'] = 'reports\\{}-隐写保密性测试-BIN文件.txt'.format(target_name)
    fc = FlowChart(prerequisite=params)
    fc.load_map(hook_script='binwalk_scan.py', map_json='隐写保密性测试.pos')
    end = False
    while not end:
        end = fc.run_step()
    fc.params_bus['binwalk']['target_file'] = filename_rom
    fc.params_bus['binwalk']['save_txt'] = 'reports\\{}-隐写保密性测试-ROM文件.txt'.format(target_name)
    fc.restart()
    end = False
    while not end:
        end = fc.run_step()
    fc.params_bus['webhook'] = {
        'webhook_url': 'https://open.feishu.cn/open-apis/bot/v2/hook/49487983-e106-49c8-a527-4b8a4dfeddf5',
        'send_string': '{}的隐写保密性测试已完成'.format(target_name)
    }
    fc.params_bus = webhook_send(params=fc.params_bus)
    os.abort()
