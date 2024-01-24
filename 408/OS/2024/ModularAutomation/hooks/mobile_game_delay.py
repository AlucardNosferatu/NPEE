import datetime
import time


def h0(params):
    offline = 'filename' in params['cv'].keys()
    params['if_switch'] = offline
    if not offline:
        uid = input('输入手机UID，可用adb devices查看确认:')
        params['android'] = {
            'uid': uid,
            'device_action': 'screenshot'
        }
    return params


def h1(params):
    return params


def h2(params):
    return params


def h3(params):
    logger = params['log']['logger']
    ocr_res = params['cv']['ocr_res']
    logger.info('测得延迟:{}'.format(ocr_res))
    params['if_switch'] = 'filename' in params['cv'].keys()
    return params


def h4(params):
    params['if_switch'] = params['cv']['frame_count'] > 0
    return params


def h5(params):
    if 'skip' in params.keys():
        params['if_switch'] = params['cv']['frame_count'] % params['skip'] == 0
    else:
        params['if_switch'] = True
    return params
