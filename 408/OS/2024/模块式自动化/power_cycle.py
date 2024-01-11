import os
import time

from core.flow_chart import FlowChart
from modules.webhook_api import webhook_send

if __name__ == '__main__':
    params = {}
    params['ps'] = {
        'res_name': 'ASRL1::INSTR',
        'baud_rate': 115200,
        'acdc': 'ac',
        'freq': 50,
        'range': 150,
        'debug': True
    }
    params['excel'] = {
        'template_path': 'reports/template_pc.xlsx'
    }
    params['misc'] = {
        'ping_host': '192.168.110.1',
        'ping_times': 5
    }
    testcase_template = {
        'volt': 220, 'ton': 1, 'toff': 1, 'tgap': 1, 'max_tboot': 120,
        'max_tcheck': 60, 'max_tcheck_5g': 60, 'ssid': '@Ruijie-s69DD', 'ssid_5g': '',
        'wait_after_boot': 10,
        # 'sim_test': 'ubus call monet getstatus',
        'sim_test': 'ubus call sniffer show',
        'console_port': 'COM7', 'console_baud_rate': 115200, 'console_password': '1b762f4ae9e6a903',
        'boot_count': 0, 'boot_ok': False, 'tboot': -1.0, 'tcheck': -1.0, 'tcheck_5g': '',
        'wifi_ok': False, 'wifi_5g_ok': '', 'ping_ok': False, 'ping_5g_ok': '', 'sim_ok': ''
    }
    volt_combo = [90, 220, 264]
    ton_combo = [1.0]
    toff_combo = [0.01, 0.02, 0.05, 0.1, 0.25, 0.5, 1.0]
    tboot_combo = [120]
    tcheck_combo = [60]
    tcheck_5g_combo = [60]
    tgap_combo = [1.0]
    repeat = 30
    params['pc_testcases'] = []
    for volt in volt_combo:
        for ton in ton_combo:
            for toff in toff_combo:
                for tboot in tboot_combo:
                    for tcheck in tcheck_combo:
                        for tcheck_5g in tcheck_5g_combo:
                            for tgap in tgap_combo:
                                testcase = testcase_template.copy()
                                testcase['volt'] = volt
                                testcase['ton'] = ton
                                testcase['toff'] = toff
                                testcase['max_tboot'] = tboot
                                testcase['max_tcheck'] = tcheck
                                testcase['max_tcheck_5g'] = tcheck_5g
                                testcase['tgap'] = tgap
                                params['pc_testcases'].append(testcase)
    params['pc_report_savepath'] = 'reports/EW300T电源切变循环测试.xlsx'
    fc = FlowChart(prerequisite=params)
    fc.load_map(hook_script='power_cycle.py', map_json='电源切变循环测试.pos')
    end = False
    while not end:
        end = fc.run_step()
    fc.params_bus['webhook'] = {
        'webhook_url': 'https://open.feishu.cn/open-apis/bot/v2/hook/49487983-e106-49c8-a527-4b8a4dfeddf5',
        'send_string': '电源切变循环测试已完成'
    }
    fc.params_bus = webhook_send(params=fc.params_bus)
    os.abort()
