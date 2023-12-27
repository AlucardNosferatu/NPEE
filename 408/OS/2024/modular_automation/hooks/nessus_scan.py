import time


def h0(params):
    params['web'] = {'browser_path': r'C:\Program Files\Google\Chrome\Application\chromedriver.exe'}
    return params


def h1(params):
    nessus_params = params['nessus']
    nessus_params['scan_name'] = params['product_id']
    nessus_params['scan_hosts'] = params['scan_hosts']
    return params


def h2(params):
    time.sleep(5)
    return params


def h3(params):
    nessus_params = params['nessus']
    scan_status = nessus_params['scan_status']
    if scan_status == 'completed':
        params['if_switch'] = True
    else:
        params['if_switch'] = False
    return params


def h4(params):
    return params
