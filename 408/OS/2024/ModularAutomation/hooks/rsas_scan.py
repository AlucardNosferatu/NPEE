import time


def h0(params):
    return params


def h1(params):
    return params


def h2(params):
    time.sleep(30)
    return params


def h3(params):
    status = params['rsas']['scan_status']
    if status == 'over':
        params['if_switch'] = True
    else:
        params['if_switch'] = False
    return params


def h4(params):
    time.sleep(5)
    return params


def h5(params):
    status = params['rsas']['report_status']
    if status == 'over':
        params['if_switch'] = True
    else:
        params['if_switch'] = False
    return params
