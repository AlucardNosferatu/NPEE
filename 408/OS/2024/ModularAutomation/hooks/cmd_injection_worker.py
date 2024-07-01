import json


def h0(params):
    if 'eweb' not in params.keys():
        params['eweb'] = {}
    params['eweb']['ip'] = params['wvt']['dut_ip']
    params['eweb']['pass'] = params['wvt']['eweb_pass']
    pass_dict = {"type": "noenc", "password": params['eweb']['pass']}
    pass_str = json.dumps(obj=pass_dict)
    params['console']['send_string'] = "ac_config set -m eweb_password '{}'".format(pass_str)
    params['console']['format'] = 'str'
    params['console']['wait'] = 1
    return params


def h1(params):
    return params
