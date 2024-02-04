import time


def h0(params):
    return params


def h1(params):
    time.sleep(5)
    return params


def h2(params):
    params['web'] = {
        'proxy': 'localhost:{}'.format(params['zap']['proxy_port']),
        'browser_path': r'C:\Program Files\Google\Chrome\Application\chromedriver.exe'
    }
    return params


def h3(params):
    params['web']['goto_url'] = params['zap']['target_url']
    return params


def h4(params):
    time.sleep(10)
    if params['zap']['target_eweb_pass'] != 'NO_PASSWORD':
        params['if_switch'] = True
    else:
        params['if_switch'] = False
    return params


def h5(params):
    params['web']['find_value'] = '//*[@id="password"]'
    params['web']['input_text'] = params['zap']['target_eweb_pass']
    return params


def h6(params):
    if params['web']['exception'] is not None:
        params['if_switch'] = True
    else:
        params['if_switch'] = False
    return params


def h7(params):
    time.sleep(5)
    params['web']['find_value'] = '//*[@id="login"]'
    return params


def h8(params):
    return params


def h9(params):
    crawl_status = params['zap']['crawl_status']
    progress = int(crawl_status)
    if progress < 100:
        params['if_switch'] = False
    else:
        params['if_switch'] = True
    return params


def h10(params):
    scan_status = params['zap']['scan_status']
    progress = int(scan_status)
    if progress < 100:
        params['if_switch'] = False
    else:
        params['if_switch'] = True
    return params


def h11(params):
    time.sleep(120)
    return params
