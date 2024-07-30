import time


def h0(params):
    return params


def h1(params):
    wd_params = params['watchdog']
    ttl = wd_params['ttl']
    age = wd_params['age']
    params['if_switch'] = age > ttl
    return params


def h2(params):
    return params


def h3(params):
    time.sleep(1)
    return params
