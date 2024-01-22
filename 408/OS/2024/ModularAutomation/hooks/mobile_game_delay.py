import datetime
import time


def h0(params):
    # params['android'] = {
    #     'uid': '手机UID',
    #     'device_action': 'screenshot'
    # }
    # params['cv'] = {
    #     'point_ul': {'x': 2029, 'y': 12},
    #     'point_dr': {'x': 2109, 'y': 36}
    # }
    params['interval'] = 1
    params['cv']['delay'] = 1000
    return params


def h1(params):
    return params


def h2(params):
    logger = params['log']['logger']
    ocr_res = params['cv']['ocr_res']
    logger.info('测得延迟:{}'.format(ocr_res))
    time.sleep(params['interval'])
    return params
