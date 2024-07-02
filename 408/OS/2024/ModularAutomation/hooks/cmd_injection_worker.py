import json
import time


def h0(params):
    if 'eweb' not in params.keys():
        params['eweb'] = {}
    params['eweb']['ip'] = params['wvt']['dut_ip']
    params['eweb']['pass'] = params['wvt']['eweb_pass']
    pass_dict = {"type": "noenc", "password": params['eweb']['pass']}
    pass_str = json.dumps(obj=pass_dict)
    cmd_list = [
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
