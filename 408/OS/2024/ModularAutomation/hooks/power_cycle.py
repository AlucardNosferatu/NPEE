import json
import random
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
    logger = params['log']['logger']
    params['pc_testcase'] = params['pc_testcases'].pop(0)
    logger.info('测试参数出队:\n{}'.format(params['pc_testcase']))
    params['ps']['volt'] = params['pc_testcase']['volt']
    logger.info('电压设置为:{}'.format(params['ps']['volt']))
    return params


def h3(params):
    logger = params['log']['logger']
    ton = params['pc_testcase']['ton']
    if type(ton) is str:
        ton = ton.split(':')
        ton_lb = float(ton[1])
        ton_ub = float(ton[2])
        logger.info('随机Ton，范围：{}<=Ton<={}秒'.format(ton_lb, ton_ub))
        ton_interval = ton_ub-ton_lb
        ton = random.random()*ton_interval+ton_lb
    logger.info('保持电源打开Ton={}秒'.format(ton))
    time.sleep(ton)
    params['ps']['toggle'] = 'off'
    return params


def h4(params):
    logger = params['log']['logger']
    logger.info('保持电源关闭Toff={}秒'.format(params['pc_testcase']['toff']))
    time.sleep(params['pc_testcase']['toff'])
    params['ps']['toggle'] = 'on'
    return params


def h5(params):
    logger = params['log']['logger']
    if 'console' in params.keys() and params['console']['exception'] is not None:
        logger.error('检测到串口动作存在异常:{}'.format(repr(params['console']['exception'])))
    return params


def h6(params):
    logger = params['log']['logger']
    params['console']['read_loop'] = True
    logger.info('启动串口持续检测')
    params['console']['read_loop_callbacks'] = [check_boot]
    logger.info('串口持续检测回调函数:\n{}'.format(params['console']['read_loop_callbacks']))
    params['console']['read_loop_interval'] = 1.0
    logger.info('串口持续检测读取周期:{}'.format(params['console']['read_loop_interval']))
    return params


def check_boot(params):
    logger = params['log']['logger']
    logger.info('检查启机次数')
    if params['console']['exception'] is not None:
        logger.error('检测到串口动作存在异常:{}'.format(repr(params['console']['exception'])))
    echo_string: str = params['console']['echo_string']
    logger.info('串口打印:\n{}'.format(echo_string))
    params['pc_testcase']['boot_count'] += echo_string.count(
        'Starting kernel ...'
    )
    logger.info('检查启机完成')
    params['pc_testcase']['boot_ok'] = 'upinit_finished' in echo_string
    logger.info('启机完成?:{}'.format(params['pc_testcase']['boot_ok']))
    params['console']['read_loop'] = not params['pc_testcase']['boot_ok']
    return params


def h7(params):
    logger = params['log']['logger']
    params['misc']['timer'] = {
        'start': True,
        'stop': False
    }
    logger.info('计时器准备启动')
    return params


def h8(params):
    logger = params['log']['logger']
    while 'timer' not in params['misc'].keys() or 'time_delta' not in params['misc']['timer'].keys():
        logger.info('计时器未准备好')
    while params['misc']['timer']['time_delta'].total_seconds() < params['pc_testcase']['max_tboot']:
        if params['pc_testcase']['boot_ok']:
            break
    logger.info('计时结束')
    params['console']['read_loop'] = False
    params['misc']['timer']['stop'] = True
    params['pc_testcase']['tboot'] = params['misc']['timer']['time_delta'].total_seconds()
    logger.info('启机检查耗时:{}'.format(params['pc_testcase']['tboot']))
    params['if_switch'] = params['pc_testcase']['boot_ok']
    for thread in params['thread_pool']:
        kill_thread(thread=thread['thread_obj'])
    params['thread_pool'].clear()
    logger.info('线程池已清空')
    params['misc']['timer'].clear()
    del params['misc']['timer']
    logger.info('计时器已重置')
    return params


def h9(params):
    params['if_switch'] = params['pc_testcase']['boot_ok']
    return params


def h10(params):
    logger = params['log']['logger']
    logger.info('启机完成后等待{}秒再连接WiFi'.format(params['pc_testcase']['wait_after_boot']))
    time.sleep(params['pc_testcase']['wait_after_boot'])
    logger.info('2.4G WiFi名称:{}'.format(params['pc_testcase']['ssid']))
    params['misc']['wifi_target_ssid'] = params['pc_testcase']['ssid']
    return params


def h11(params):
    logger = params['log']['logger']
    while 'timer' not in params['misc'].keys() or 'time_delta' not in params['misc']['timer'].keys():
        logger.info('计时器未准备好')
    while params['misc']['timer']['time_delta'].total_seconds() < params['pc_testcase']['max_tcheck']:
        if 'wifi_result' in params['misc'].keys() and params['misc']['wifi_result'][0]:
            break
    logger.info('计时结束')
    params['misc']['timer']['stop'] = True
    params['pc_testcase']['tcheck'] = params['misc']['timer']['time_delta'].total_seconds()
    logger.info('2.4G WiFi连接耗时:{}'.format(params['pc_testcase']['tcheck']))
    params['pc_testcase']['wifi_ok'] = 'wifi_result' in params['misc'].keys(
    ) and params['misc']['wifi_result'][0]
    logger.info('2.4G WiFi连接成功?:{}'.format(params['pc_testcase']['wifi_ok']))
    for thread in params['thread_pool']:
        kill_thread(thread=thread['thread_obj'])
    params['thread_pool'].clear()
    logger.info('线程池已清空')
    params['misc']['timer'].clear()
    del params['misc']['timer']
    logger.info('计时器已重置')
    del params['misc']['wifi_result']
    logger.info('WiFi连接器已重置')
    return params


def h12(params):
    logger = params['log']['logger']
    params['pc_testcase']['ping_ok'] = params['misc']['ping_result'][0]
    logger.info('2.4G 网关可PING通?:{}'.format(params['pc_testcase']['ping_ok']))
    params['if_switch'] = len(params['pc_testcase']['ssid_5g']) > 0
    logger.info('测试5G?:{}'.format(len(params['pc_testcase']['ssid_5g']) > 0))
    return params


def h13(params):
    if len(params['pc_testcase']['ssid_5g']) > 0:
        logger = params['log']['logger']
        params['pc_testcase']['ping_5g_ok'] = params['misc']['ping_result'][0]
        logger.info('5G 网关可PING通?:{}'.format(params['pc_testcase']['ping_5g_ok']))
    params['if_switch'] = len(params['pc_testcase']['sim_test']) > 0
    return params


def h14(params):
    logger = params['log']['logger']
    logger.info('5G WiFi名称:{}'.format(params['pc_testcase']['ssid_5g']))
    params['misc']['wifi_target_ssid'] = params['pc_testcase']['ssid_5g']
    return params


def h15(params):
    logger = params['log']['logger']
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
    logger.info('使用以下参数登录控制台:\n{}'.format(params['console']))
    return params


def h16(params):
    logger = params['log']['logger']
    echo_string = params['console']['echo_string']
    logger.info('控制台命令回显:\n{}'.format(echo_string))
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
    logger.info('SIM模块测试结果:{}'.format(params['pc_testcase']['sim_ok']))
    return params


def h17(params):
    logger = params['log']['logger']
    if 'pc_results' not in params.keys():
        params['pc_results'] = {}
        for key in params['pc_testcase'].keys():
            params['pc_results'][key] = []
    logger.info('开始整理测试结果，目前已进行{}轮'.format(len(params['pc_results']['volt'])))
    for key in params['pc_testcase'].keys():
        params['pc_results'][key].append(params['pc_testcase'][key])
    params['excel']['data_src_dict'] = params['pc_results']
    params['excel']['save_path'] = params['pc_report_savepath']
    logger.info('测试结果将写入:{}'.format(params['excel']['save_path']))
    return params


def h18(params):
    logger = params['log']['logger']
    logger.info('启机测试结果:{}'.format(params['pc_testcase']['boot_ok']))
    if params['pc_testcase']['boot_ok']:
        logger.info('2.4G连通性测试结果:{}'.format(params['pc_testcase']['ping_ok']))
        if params['pc_testcase']['ping_ok']:
            if 'ping_5g_ok' in params['pc_testcase'].keys():
                logger.info('5G连通性测试结果:{}'.format(params['pc_testcase']['ping_5g_ok']))
                if params['pc_testcase']['ping_5g_ok']:
                    params['if_switch'] = True
                else:
                    params['if_switch'] = False
            else:
                params['if_switch'] = True
        else:
            params['if_switch'] = False
    else:
        params['if_switch'] = False
    logger.info('本轮测试通过？:{}'.format(params['if_switch']))
    logger.info('剩余测试轮数:{}'.format(len(params['pc_testcases'])))
    if params['if_switch']:
        params['if_switch'] = len(params['pc_testcases']) > 0
    logger.info('继续测试？:{}'.format(params['if_switch']))
    return params


def h19(params):
    logger = params['log']['logger']
    params['pc_testcase']['boot_ok'] = params['console']['exception'] is None
    logger.info('登录测试启机成功?:{}'.format(params['pc_testcase']['boot_ok']))
    return params


def h20(params):
    logger = params['log']['logger']
    logger.info('保持电源关闭Tgap={}秒'.format(params['pc_testcase']['tgap']))
    time.sleep(params['pc_testcase']['tgap'])
    params['ps']['toggle'] = 'on'
    return params


def h21(params):
    logger = params['log']['logger']
    while 'timer' not in params['misc'].keys() or 'time_delta' not in params['misc']['timer'].keys():
        logger.info('计时器未准备好')
    while params['misc']['timer']['time_delta'].total_seconds() < params['pc_testcase']['max_tcheck_5g']:
        if 'wifi_result' in params['misc'].keys() and params['misc']['wifi_result'][0]:
            break
    logger.info('计时结束')
    params['misc']['timer']['stop'] = True
    params['pc_testcase']['tcheck_5g'] = params['misc']['timer']['time_delta'].total_seconds()
    logger.info('5G WiFi连接耗时:{}'.format(params['pc_testcase']['tcheck_5g']))
    params['pc_testcase']['wifi_5g_ok'] = 'wifi_result' in params['misc'].keys(
    ) and params['misc']['wifi_result'][0]
    logger.info('5G WiFi连接成功?:{}'.format(params['pc_testcase']['wifi_5g_ok']))
    for thread in params['thread_pool']:
        kill_thread(thread=thread['thread_obj'])
    params['thread_pool'].clear()
    logger.info('线程池已清空')
    params['misc']['timer'].clear()
    del params['misc']['timer']
    logger.info('计时器已重置')
    del params['misc']['wifi_result']
    logger.info('WiFi连接器已重置')
    return params


def h22(params):
    logger = params['log']['logger']
    logger.info('以非登录方式打开串口，监听启机日志')
    params['console'] = {
        'console_type': 'serial',
        'port': params['pc_testcase']['console_port'],
        'baud_rate': params['pc_testcase']['console_baud_rate'],
        'serial_type': 'LISTENER'
    }
    return params


def h23(params):
    logger = params['log']['logger']
    logger.info('关闭电源，本轮测试结束')
    params['ps']['toggle'] = 'off'
    return params
