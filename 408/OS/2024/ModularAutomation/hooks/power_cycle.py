import datetime
import json
import time
from kill_thread import kill_thread
time_format = "%Y年%m月%d日-%H时%M分%S秒"


def h0(params):
    params['ps'] = {
        'res_name': 'ASRL1::INSTR',
        'baud_rate': 115200,
        'acdc': 'ac',
        'freq': 50,
        'range': 150,
    }
    params['excel'] = {
        'template_path': 'reports/template_pc.xlsx'
    }
    params['misc'] = {
        'ping_host': '192.168.110.1',
        'ping_times': 5
    }
    params['pc_testcases'] = [
        {
            'volt': 220, 'ton': 10, 'toff': 1, 'tgap': 10, 'max_tboot': 50,
            'max_tcheck': 50, 'max_tcheck_5g': 50, 'ssid': 'EW300T', 'ssid_5g': 'EW300T_5G',
            'sim_test': True,
            'console_port': 'COM5', 'console_baud_rate': 57600, 'console_password': '57e541f69676ce62'
        }
    ]
    params['pc_report_savepath'] = 'reports/EW300T电源切变循环测试.xlsx'
    return params


def h1(params):
    time.sleep(1)
    return params


def h2(params):
    params['pc_testcase'] = params['pc_testcases'].pop(0)
    params['ps']['volt'] = params['pc_testcase']['volt']
    return params


def h3(params):
    time.sleep(params['pc_testcase']['ton'])
    params['ps']['toggle'] = 'off'
    return params


def h4(params):
    time.sleep(params['pc_testcase']['toff'])
    params['ps']['toggle'] = 'on'
    return params


def h5(params):
    return params


def h6(params):
    params['console']['read_loop'] = True
    params['console']['read_loop_callbacks'] = [check_boot]
    params['console']['read_loop_interval'] = 1.0
    return params


def check_boot(params):
    echo_string: str = params['console']['echo_string']
    params['pc_testcase']['boot_count'] += echo_string.count(
        'Starting kernel ...'
    )
    params['pc_testcase']['boot_ok'] = '=============upinit_finished================' in echo_string
    params['console']['read_loop'] = not params['pc_testcase']['boot_ok']
    return params


def h7(params):
    params['misc']['timer'] = {
        'start': True,
        'stop': False
    }
    print('计时器准备启动')
    return params


def h8(params):
    while 'timer' not in params['misc'].keys() or 'time_delta' not in params['misc']['timer'].keys():
        pass
    while params['misc']['timer']['time_delta'].total_seconds() < params['pc_testcase']['max_tboot']:
        if params['pc_testcase']['boot_ok']:
            break
    params['console']['read_loop'] = False
    params['misc']['timer']['stop'] = True
    params['pc_testcase']['tboot'] = params['misc']['timer']['time_delta'].total_seconds()
    params['if_switch'] = params['pc_testcase']['boot_ok']
    for thread in params['thread_pool']:
        kill_thread(thread=thread['thread_obj'])
    params['thread_pool'].clear()
    del params['misc']['timer']
    return params


def h9(params):
    params['if_switch'] = params['pc_testcase']['boot_ok']
    return params


def h10(params):
    time.sleep(params['pc_testcase']['wait_after_boot'])
    params['misc']['wifi_target_ssid'] = params['pc_testcase']['ssid']
    return params


def h11(params):
    while 'timer' not in params['misc'].keys() or 'time_delta' not in params['misc']['timer'].keys():
        pass
    while params['misc']['timer']['time_delta'].total_seconds() < params['pc_testcase']['max_tcheck']:
        if 'wifi_result' in params['misc'].keys() and params['misc']['wifi_result'][0]:
            break
    params['misc']['timer']['stop'] = True
    params['pc_testcase']['tcheck'] = params['misc']['timer']['time_delta'].total_seconds()
    params['pc_testcase']['wifi_ok'] = 'wifi_result' in params['misc'].keys(
    ) and params['misc']['wifi_result'][0]
    for thread in params['thread_pool']:
        kill_thread(thread=thread['thread_obj'])
    params['thread_pool'].clear()
    del params['misc']['timer']
    return params


def h12(params):
    params['pc_testcase']['ping_ok'] = params['misc']['ping_result'][0]
    params['if_switch'] = len(params['pc_testcase']['ssid_5g']) > 0
    return params


def h13(params):
    params['pc_testcase']['ping_5g_ok'] = params['misc']['ping_result'][0]
    params['if_switch'] = len(params['pc_testcase']['sim_test']) > 0
    return params


def h14(params):
    params['misc']['wifi_target_ssid'] = params['pc_testcase']['ssid_5g']
    return params


def h15(params):
    params['console'] = {
        'console_type': 'serial',
        'port': params['pc_testcase']['console_port'],
        'baud_rate': params['pc_testcase']['console_baud_rate'],
        'serial_pass': params['pc_testcase']['console_password'],
        'serial_type': 'RJ',
        'send_string': params['pc_testcase']['sim_test'],
        'format': 'str',
        'wait': 2
    }
    return params


def h16(params):
    echo_string = params['console']['echo_string']
    echo_string = echo_string.split('\r\n')
    while not echo_string[0].startswith('{'):
        echo_string.pop(0)
    while not echo_string[-1].startswith('}'):
        echo_string.pop(-1)
    echo_string = '\r\n'.join(echo_string)
    sim_dict = json.loads(echo_string)
    if 'sim' in sim_dict.keys() and 'band' in sim_dict.keys():
        params['pc_testcase']['sim_ok'] = sim_dict['sim'] == 'SIM NOT INSERTED' and sim_dict['band'] != ''
    else:
        params['pc_testcase']['sim_ok'] = False
    return params


def h17(params):
    if 'pc_results' not in params.keys():
        params['pc_results'] = {}
        for key in params['pc_testcase'].keys():
            params['pc_results'][key] = []
    for key in params['pc_testcase'].keys():
        params['pc_results'][key].append(params['pc_testcase'][key])
    params['excel']['data_src_dict'] = params['pc_results']
    params['excel']['save_path'] = params['pc_report_savepath']
    return params


def h18(params):
    params['if_switch'] = len(params['pc_testcases']) > 0
    return params


def h19(params):
    params['pc_testcase']['boot_ok'] = params['console']['exception'] is None
    return params


def h20(params):
    time.sleep(params['pc_testcase']['tgap'])
    params['ps']['toggle'] = 'on'
    return params


def h21(params):
    while 'timer' not in params['misc'].keys() or 'time_delta' not in params['misc']['timer'].keys():
        pass
    while params['misc']['timer']['time_delta'].total_seconds() < params['pc_testcase']['max_tcheck_5g']:
        if 'wifi_result' in params['misc'].keys() and params['misc']['wifi_result'][0]:
            break
    params['misc']['timer']['stop'] = True
    params['pc_testcase']['tcheck_5g'] = params['misc']['timer']['time_delta'].total_seconds()
    params['pc_testcase']['wifi_5g_ok'] = 'wifi_result' in params['misc'].keys(
    ) and params['misc']['wifi_result'][0]
    for thread in params['thread_pool']:
        kill_thread(thread=thread['thread_obj'])
    params['thread_pool'].clear()
    del params['misc']['timer']
    return params


def h22(params):
    params['console'] = {
        'console_type': 'serial',
        'port': params['pc_testcase']['console_port'],
        'baud_rate': params['pc_testcase']['console_baud_rate'],
        'serial_type': 'LISTENER'
    }
    return params


def h23(params):
    params['ps']['toggle'] = 'off'
    return params
