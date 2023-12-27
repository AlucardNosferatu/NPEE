import os

from core.flow_chart import FlowChart
from modules.webhook_api import webhook_send

if __name__ == '__main__':
    params = {
        'project_id': 'OW3.0PR5_R303', 'product_id': 'EW1300G-ExtDDR', 'baseline_project': 'OW3.0PR5_R222',
        'bin_url': 'http://10.101.7.24:20290/%E6%B5%B7%E5%A4%96/EW1300G-ExtDDR-R303/%E5%8D%87%E7%BA%A7%E6%96%87%E4%BB%B6/EW_3.0%281%29B11P303_EW1300GI_10242013_install.bin',
        'web': {'browser_path': r'C:\Program Files\Google\Chrome\Application\chromedriver.exe'},
        'dont_create': True
    }
    fc = FlowChart(prerequisite=params)
    fc.load_map(hook_script='bin_scan.py', map_json='二进制静态测试.pos')
    end = False
    while not end:
        end = fc.run_step()
    fc.params_bus['webhook'] = {
        'webhook_url': 'https://open.feishu.cn/open-apis/bot/v2/hook/49487983-e106-49c8-a527-4b8a4dfeddf5',
        'send_string': 'SCA测试已完成'
    }
    fc.params_bus = webhook_send(params=fc.params_bus)
    os.abort()
