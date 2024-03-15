import json
import os

from core.flow_chart import FlowChart
from modules.logger import log_logger_init, log_handler_init
from modules.webhook_api import webhook_send

if __name__ == '__main__':
    params_from_json = json.loads(
        s='\n'.join(
            open(
                file='reports/power_cycle.json',
                mode='r', encoding='utf-8'
            ).readlines()
        )
    )
    params = {
        'ps': {
            'res_name': params_from_json['pcr']['res_name'],
            'baud_rate': params_from_json['pcr']['baud_rate'],
            'acdc': 'ac',
            'freq': params_from_json['pcr']['freq'],
            'range': params_from_json['pcr']['range'],
            'debug': params_from_json['pcr']['debug']
        },
        'excel': {
            'template_path': 'reports/template_pc.xlsx'
        },
        'misc': {
            'ping_host': params_from_json['dut']['lan_ip'],
            'ping_times': params_from_json['dut']['ping_times']
        }
    }
    testcase_template = {
        'volt': 220, 'ton': 1, 'toff': 1, 'tgap': 1, 'max_tboot': 120,
        'max_tcheck': 60, 'max_tcheck_5g': 60, 'ssid': params_from_json['dut']['ssid'],
        'ssid_5g': params_from_json['dut']['ssid_5g'],
        'wait_after_boot': params_from_json['test']['wait_after_boot'],
        'sim_test': params_from_json['dut']['sim_test'],
        'console_port': params_from_json['dut']['port'], 'console_baud_rate': params_from_json['dut']['baud_rate'],
        'console_password': params_from_json['dut']['console_password'],
        'boot_count': 0, 'boot_ok': False, 'tboot': -1.0, 'tcheck': -1.0, 'tcheck_5g': '',
        'wifi_ok': False, 'wifi_5g_ok': '', 'ping_ok': False, 'ping_5g_ok': '', 'sim_ok': ''
    }
    volt_combo = params_from_json['test']['volt_combo']
    ton_combo = params_from_json['test']['ton_combo']
    toff_combo = params_from_json['test']['toff_combo']
    tboot_combo = params_from_json['test']['tboot_combo']
    tcheck_combo = params_from_json['test']['tcheck_combo']
    tcheck_5g_combo = params_from_json['test']['tcheck_5g_combo']
    tgap_combo = params_from_json['test']['tgap_combo']
    repeat = params_from_json['test']['repeat']
    params['pc_testcases'] = []
    for volt in volt_combo:
        for ton in ton_combo:
            for toff in toff_combo:
                for tboot in tboot_combo:
                    for tcheck in tcheck_combo:
                        for tcheck_5g in tcheck_5g_combo:
                            for tgap in tgap_combo:
                                for _ in range(repeat):
                                    testcase = testcase_template.copy()
                                    testcase['volt'] = volt
                                    testcase['ton'] = ton
                                    testcase['toff'] = toff
                                    testcase['max_tboot'] = tboot
                                    testcase['max_tcheck'] = tcheck
                                    testcase['max_tcheck_5g'] = tcheck_5g
                                    testcase['tgap'] = tgap
                                    params['pc_testcases'].append(testcase)
    params['pc_report_savepath'] = params_from_json['pc_report_savepath']
    fc = FlowChart(prerequisite=params)
    fc.load_map(hook_script='power_cycle.py', map_json='电源切变循环测试.pos')
    # todo: makeshift patch
    fc.params_bus['log'] = {'logger_name': 'power_cycle', 'log_backup_count': 8192}
    fc.params_bus = log_logger_init(params=fc.params_bus)
    fc.params_bus = log_handler_init(params=fc.params_bus)
    end = False
    while not end:
        end = fc.run_step()
    fc.params_bus['webhook'] = {
        'webhook_url': params_from_json['webhook_url'],
        'send_string': '电源切变循环测试已完成'
    }
    fc.params_bus = webhook_send(params=fc.params_bus)
    os.abort()
