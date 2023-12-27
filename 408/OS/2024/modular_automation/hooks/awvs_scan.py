import time


def h0(params):
    return params


def h1(params):
    return params


def h2(params):
    time.sleep(30)
    return params


def h3(params):
    scan_status = params['awvs']['scan_status']
    if scan_status.lower() in ['completed', 'aborted']:
        params['if_switch'] = True
    else:
        params['if_switch'] = False
    return params


def h4(params):
    time.sleep(5)
    return params


def h5(params):
    report_status = params['awvs']['report_status']
    if report_status.lower() == 'completed':
        params['if_switch'] = True
    else:
        params['if_switch'] = False
    return params
