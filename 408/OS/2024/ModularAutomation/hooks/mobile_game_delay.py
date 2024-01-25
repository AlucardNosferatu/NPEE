import datetime
import time


def h0(params):
    # params['cv']['point_ul'] = {'x': 2289, 'y': 12}
    # params['cv']['point_dr'] = {'x': 2369, 'y': 36}
    params['cv']['point_ul'] = {'x': 25, 'y': 25}
    params['cv']['point_dr'] = {'x': 125, 'y': 50}
    params['cv']['delay'] = 1
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


def h6(params):
    params['if_switch'] = 'flowchart' in params.keys()
    if params['if_switch']:
        params['flowchart']['new_fc_pre']['cv'] = params['cv'].copy()
    return params


def h7(params):
    params['if_switch'] = params['flowchart']['end_status'][params['flowchart']['old_fc_name']]
    if params['if_switch']:
        params['cv'] = params['flowchart']['fc_pools'][params['flowchart']['old_fc_name']].params_bus['cv'].copy()
    return params
