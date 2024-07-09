import json
import pickle
import re
import time

debug = False


def h0(params):
    if 'eweb' not in params.keys():
        params['eweb'] = {}
    params['eweb']['ip'] = params['wvt']['dut_ip']
    params['eweb']['pass'] = params['wvt']['eweb_pass']
    pass_dict = {"type": "noenc", "password": params['eweb']['pass']}
    pass_str = json.dumps(obj=pass_dict)
    nid_dict = {"networkId": "0"}
    nid_str = json.dumps(obj=nid_dict)
    cmd_list = [
        "dev_sta set -m deviceMove '{}'".format(nid_str),
        "ac_config set -m eweb_password '{}'".format(pass_str),
        'uci set luci.main.loginNum="0"',
        "uci commit"
    ]
    if debug:
        params['console']['send_string'] = 'cd'
    else:
        params['console']['send_string'] = '\r'.join(cmd_list)
    params['console']['format'] = 'str'
    if debug:
        params['console']['wait'] = 0.5
    else:
        params['console']['wait'] = 1
    return params


def h1(params):
    if not debug:
        time.sleep(0.5)
    if 'eweb' not in params.keys():
        params['eweb'] = {}
    params['eweb']['repost_retry'] = 5
    return params


def h2(params):
    logger = params['log']['logger']
    params['if_switch'] = params['eweb']['exception'] is not None
    if params['if_switch'] and 'repost_retry' in params['eweb'].keys() and params['eweb']['repost_retry'] <= 0:
        logger.warn('重试次数已耗尽，接口:\n{}\n可能不存在!'.format(params['eweb']['repost_cache']))
        params['if_switch'] = False
    return params


def h3(params):
    params['eweb']['repost_again'] = True
    params['eweb']['repost_retry'] -= 1
    return params


def h4(params):
    params['if_switch'] = params['console']['exception'] is not None
    return params


def h5(params):
    return params


def h6(params):
    if debug:
        params['console']['send_string'] = 'cd'
        params['console']['wait'] = 0.125
    else:
        params['console']['send_string'] = 'top -bn1'
        params['console']['wait'] = 1
    params['console']['format'] = 'str'
    return params


def h7(params):
    logger = params['log']['logger']
    echo_string = params['console']['echo_string']
    if debug:
        params['if_switch'] = False
    else:
        try:
            cpu_pattern = r'\b(\d+)%\s+idle'
            cpu_idle = re.search(cpu_pattern, echo_string)
            cpu_idle = float(cpu_idle.group(1))
            memory_pattern = r"Mem:\s+([\d]+)K\s+used,\s+([\d]+)K\s+free"
            memory_usage = re.search(memory_pattern, echo_string)
            memory_used = int(memory_usage.group(1))
            memory_free = int(memory_usage.group(2))
            # 检查资源是否不足20%
            if cpu_idle < 10 or (memory_free / (memory_used + memory_free)) * 100 < 5:
                logger.warn("Warning: Resource usage is high!")
                params['if_switch'] = True
            else:
                logger.info("Resource usage is within acceptable limits.")
                params['if_switch'] = False
        except Exception as e:
            logger.error("Error occurred while parsing echo of top -bn1:{}".format(repr(e)))
            params['if_switch'] = True
    return params


def h8(params):
    params['console']['send_string'] = 'reboot'
    params['console']['format'] = 'str'
    params['console']['wait'] = 0
    return params


def h9(params):
    time.sleep(60)
    params = h11(params=params)
    return params


def h10(params):
    misc_params = params['misc']
    ping_result = misc_params['ping_result']
    params['if_switch'] = ping_result[0]
    return params


def h11(params):
    params = h15(params=params)
    params['wvt']['ping_device_retry'] = 5
    return params


def h12(params):
    params['wvt']['reboot_check_retry'] -= 1
    params['if_switch'] = params['wvt']['reboot_check_retry'] < 0
    time.sleep(0.5)
    return params


def h13(params):
    logger = params['log']['logger']
    with open(file=params['wvt']['checkpoint_path'], mode='wb') as f:
        pickle.dump(obj=params['wvt'], file=f)
    logger.info('已保存断点续测存档')
    params['wvt']['reboot_check_retry'] = 5
    return params


def h14(params):
    params['wvt']['ping_device_retry'] -= 1
    params['if_switch'] = params['wvt']['ping_device_retry'] < 0
    return params


def h15(params):
    time.sleep(4)
    params['misc'] = {
        'ping_host': params['wvt']['dut_ip'],
        'ping_times': 5
    }
    return params
