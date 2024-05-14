import json
import time


def h0(params):
    # params['mqtt'] = {
    #     'host': '10.51.132.73',
    #     'topic': 'sys/#'
    # }
    # params['sn'] = 'G1RP9XT005007'
    # params['product'] = 'X60-PRO'
    # params['save_txt'] = 'reports/{}加密MQTT通信测试.txt'
    return params


def h1(params):
    logger = params['log']['logger']
    count = 0
    while count < 10 and 'exception' not in params['mqtt'].keys():
        logger.info('等待连接')
        time.sleep(1)
        count += 1
    if count >= 10:
        params['mqtt']['exception'] = TimeoutError('连接超时')
    params['if_switch'] = params['mqtt']['exception'] is None
    return params


def h2(params):
    return params


def h3(params):
    target = ['设备地址:', params['mqtt']['host'], '设备型号:', params['product'], '设备序列号:', params['sn']]
    target = '\n'.join(target)
    failed = False
    exception = '是否出现异常？:\n'
    if params['mqtt']['exception'] is not None:
        exception += repr(params['mqtt']['exception'])
    else:
        exception += '无异常（未加密连接应当失败，与预期不符）'
        failed = True
    scan_output = []
    if 'msg_queue' in params['mqtt'].keys() and len(params['mqtt']['msg_queue']) > 0:
        while len(params['mqtt']['msg_queue']) > 0:
            msg = params['mqtt']['msg_queue'].pop(0)
            msg = msg.payload.decode('utf-8')
            if params['sn'] in msg:
                scan_output.append('####检测到设备SN！加密未生效！####')
                failed = True
            if params['product'] in msg:
                scan_output.append('####检测到设备型号信息！加密未生效！####')
                failed = True
            data = json.loads(s=msg)
            formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
            scan_output.append(formatted_json)
    else:
        scan_output = []
    scan_output.insert(0, 'MQTT话题记录:')
    scan_output = '\n'.join(scan_output)
    if failed:
        conclusion = '结论：测试不通过'
    else:
        conclusion = '结论：测试通过'
    report = '\n===================================\n'.join(
        [target, conclusion, exception, scan_output]
    )
    with open(params['save_txt'], 'w') as f:
        f.writelines(report)
    return params


def h4(params):
    time.sleep(10)
    return params
