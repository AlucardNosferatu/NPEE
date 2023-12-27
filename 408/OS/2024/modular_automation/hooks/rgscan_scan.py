import time


def h0(params):
    return params


def h1(params):
    return params


def h2(params):
    time.sleep(30)
    return params


def h3(params):
    scan_status = params['rgscan']['scan_status']
    progress = int(scan_status['aaData'][0][5].split('_')[-1])
    if progress < 100:
        params['if_switch'] = False
    else:
        params['if_switch'] = True
    return params
