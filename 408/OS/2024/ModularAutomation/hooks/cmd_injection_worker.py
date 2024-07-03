import json
import re
import time


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
    params['console']['send_string'] = '\r\n'.join(cmd_list)
    params['console']['format'] = 'str'
    params['console']['wait'] = 1
    time.sleep(1)
    return params


def h1(params):
    time.sleep(1)
    return params


def h2(params):
    params['if_switch'] = params['eweb']['exception'] is not None
    return params


def h3(params):
    params['eweb']['repost_again'] = True
    return params


def h4(params):
    params['if_switch'] = params['console']['exception'] is not None
    return params


def h5(params):
    return params


def h6(params):
    params['console']['send_string'] = 'top -bn1'
    params['console']['format'] = 'str'
    params['console']['wait'] = 2
    return params


def h7(params):
    echo_string = params['console']['echo_string']
    try:
        cpu_pattern = r'\b(\d+)%\s+idle'
        cpu_idle = re.search(cpu_pattern, echo_string)
        cpu_idle = float(cpu_idle.group(1))
        memory_pattern = r"Mem:\s+([\d]+)K\s+used,\s+([\d]+)K\s+free"
        memory_usage = re.search(memory_pattern, echo_string)
        memory_used = int(memory_usage.group(1))
        memory_free = int(memory_usage.group(2))
        # 检查资源是否不足20%
        if cpu_idle < 15 or (memory_free / (memory_used + memory_free)) * 100 < 5:
            print("Warning: Resource usage is high!")
            params['if_switch'] = True
        else:
            print("Resource usage is within acceptable limits.")
            params['if_switch'] = False
    except Exception as e:
        print("Error occurred while parsing echo of top -bn1:{}".format(repr(e)))
        params['if_switch'] = True
    return params


def h8(params):
    params['console']['send_string'] = 'reboot'
    params['console']['format'] = 'str'
    params['console']['wait'] = 0.5
    return params


def h9(params):
    time.sleep(90)
    params['misc'] = {
        'ping_host': params['wvt']['dut_ip'],
        'ping_times': 10
    }
    return params


def h10(params):
    misc_params = params['misc']
    ping_result = misc_params['ping_result']
    params['if_switch'] = ping_result[0]
    return params


def h11(params):
    time.sleep(2)
    params['misc'] = {
        'ping_host': params['wvt']['dut_ip'],
        'ping_times': 10
    }
    return params
