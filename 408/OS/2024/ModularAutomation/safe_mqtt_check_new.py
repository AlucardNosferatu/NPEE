import copy
import datetime
import json
import pickle
import random
import string
import time

import openpyxl

from hooks.cmd_injection import walk_cmd_dict, set_cmd_dict
from modules.console import console_login, console_send
from modules.mqtt_api import mqtt_init, mqtt_publish


def get_timestamp_now():
    timestamp = int(time.time())
    return timestamp


topics = {
    'sys/001/AP/': {
        '#MODEL#/#SN#/groupid': None,
        '#MODEL#/#SN#/inform': {
            "type": "inform", "typeid": 2, "code": 0,
            "msg": {
                "band": "2.4G,5G", "channf": "-85,-91", "chutil": "30,20", "channel": "6,48",
                "txpower": "75,75", "cur_channel": "6,48", "cac_time": "0,0", "product": "EHR",
                "deviceType": "H30M", "devModel": "H30M", "deviceSn": "G1SK4AT00061B",
                "ip": "192.168.1.49", "mac": "F0:74:8D:5D:04:E0", "periodInformInterval": 30,
                "informPeriod": 30, "hardware": "1.00",
                "software": "ReyeeOS 1.239.1607;EW_3.0(1)B11P239,Release(11160715)", "os": "OW",
                "networkId": "dev_F0:74:8D:5D:01:0C_1720061321",
                "networkName": "EWEB_F0748D5D010C", "groupId": "0", "groupName": "default",
                "parentGroupId": "", "forwardMode": "AP", "relayMode": "wirelessBridge",
                "hostName": "Ruijie", "staNum": 0, "startTime": "2024-10-24 15:49:43",
                "currentTime": "2024-11-13 15:50:19",
                "configId": {
                    "rootPath": "\/etc\/rg_config\/global\/",
                    "configversion": [
                        {
                            "networkId": "dev_F0:74:8D:5D:01:0C_1720061321", "configId": "1731482142",
                            "currentTime": "1731482142", "groupId": "0", "configTime": "1731482142",
                            "module": "tmngt", "subConfigId": "1731482142_G1SP4UV001075",
                            "moduleId": "13"
                        },
                        {
                            "networkId": "dev_F0:74:8D:5D:01:0C_1720061321", "configId": "1730079519",
                            "currentTime": "1730079519", "groupId": "0", "configTime": "1730079519",
                            "module": "wireless", "subConfigId": "1725260178_G1SP4UV001075",
                            "moduleId": "1"
                        },
                        {
                            "networkId": "dev_F0:74:8D:5D:01:0C_1720061321", "configId": "1725260140",
                            "currentTime": "1725260177", "groupId": "0", "configTime": "1725260140",
                            "module": "timezone", "subConfigId": "1725260176_G1SP4UV001075",
                            "moduleId": "2"
                        },
                        {
                            "networkId": "dev_F0:74:8D:5D:01:0C_1720061321", "configId": "1720061321",
                            "currentTime": "1720061321", "groupId": "0", "configTime": "1720061321",
                            "module": "network_group", "subConfigId": "1720061321_G1SP4UV001075",
                            "moduleId": "6"
                        },
                        {
                            "networkId": "dev_F0:74:8D:5D:01:0C_1720061321", "configId": "0",
                            "currentTime": "0", "groupId": "0", "configTime": "0", "module": "kvNavAc",
                            "subConfigId": "1723013935_G1SP4UV001075", "moduleId": "224"
                        },
                        {
                            "networkId": "dev_F0:74:8D:5D:01:0C_1720061321", "configId": "1725260141",
                            "currentTime": "1725260179", "groupId": "0", "configTime": "1725260141",
                            "module": "eweb_password", "subConfigId": "1725260179_G1SP4UV001075",
                            "moduleId": "7"
                        },
                        {
                            "networkId": "dev_F0:74:8D:5D:01:0C_1720061321", "configId": "0",
                            "currentTime": "0", "groupId": "0", "configTime": "0",
                            "module": "wirelessMacFilter", "subConfigId": "1720061341_G1SP4UV001075",
                            "moduleId": "10"
                        },
                        {
                            "networkId": "dev_F0:74:8D:5D:01:0C_1720061321", "configId": "0",
                            "currentTime": "0", "groupId": "0", "configTime": "0",
                            "module": "ntpserver", "subConfigId": "1720061341_G1SP4UV001075",
                            "moduleId": "3"
                        },
                        {
                            "networkId": "dev_F0:74:8D:5D:01:0C_1720061321", "configId": "0",
                            "currentTime": "0", "groupId": "0", "configTime": "0", "module": "wirelan",
                            "subConfigId": "1720061341_G1SP4UV001075", "moduleId": "11"
                        },
                        {
                            "networkId": "dev_F0:74:8D:5D:01:0C_1720061321", "configId": "0",
                            "currentTime": "0", "groupId": "0", "configTime": "0", "module": "devLed",
                            "subConfigId": "1720061341_G1SP4UV001075", "moduleId": "15"
                        },
                        {
                            "networkId": "dev_F0:74:8D:5D:01:0C_1720061321", "configId": "0",
                            "currentTime": "0", "groupId": "0", "configTime": "0", "module": "roam",
                            "subConfigId": "1720061341_G1SP4UV001075", "moduleId": "51"
                        },
                        {
                            "networkId": "dev_F0:74:8D:5D:01:0C_1720061321", "configId": "0",
                            "currentTime": "0", "groupId": "0", "configTime": "0",
                            "module": "timeReboot", "subConfigId": "1720061341_G1SP4UV001075",
                            "moduleId": "12"
                        }
                    ]
                }
            }
        },
        '#MODEL#/#SN#/setnetworkId': None,
        '#MODEL#/#SN#/stalog': {
            "type": "stalog", "typeid": 4, "code": 0,
            "msg": {
                "sn": "G1SK4AT00061B", "deviceAliasName": "Ruijie", "groupId": "0", "stalogPeroid": 30, "list": []
            }
        },
        'rpc/shell/request/#TIMESTAMP#': None,
        'rpc/shell/response/#TIMESTAMP#': None
    },
    'sys/FFFF/': {
        'master': {
            "sn": "G1SP4UV001075", "devModel": "EW3000GX-PRO", "mac": "F0:74:8D:5D:01:0C",
            "software": "ReyeeOS 1.261.2122;EW_3.0(1)B11P261,Release(11212218)", "protoVer": 3
        },
        'wifi_diag_start': None,
        'wifi_diag_result': None
    }
}


def read_payloads(filename='reports/payloads.xlsx'):
    # 打开 Excel 文件
    wb = openpyxl.load_workbook(filename)
    sheet = wb.active  # 选择当前活动的工作表
    # 初始化一个空的列表来存储数据
    payloads = []
    # 从第一列开始遍历
    for row in sheet.iter_rows(min_col=1, max_col=1, values_only=True):
        # row 是一个包含单元格值的元组
        cell_value = row[0]
        # 如果遇到 '#END_OF_COL'，则停止
        if cell_value == '#END_OF_COL':
            break
        # 将当前单元格的值添加到数据列表中
        payloads.append(cell_value)
    return payloads


def empty_payload_test(broker_ip, ssh_password, topic_prefix, topic_postfix):
    topic_template = topic_prefix + topic_postfix
    topic = topic_template.replace('#MODEL#', slave_model)
    topic = topic.replace('#SN#', salve_sn)
    topic = topic.replace('#TIMESTAMP#', str(get_timestamp_now()))
    print('测试topic:', topic)
    empty_payload_pass = True
    params = {
        'mqtt': {
            'host': broker_ip,
            'topic': topic,
            'payload': None
        },
        'console': {
            'console_type': 'ssh',
            'dut_ip': ip,
            'ssh_pass': ssh_password
        }
    }
    params = console_login(params=params)
    params = mqtt_init(params=params)
    params['console']['send_string'] = 'echo > /tmp/mqtt/mqtt.log'
    params = console_send(params=params)
    params = mqtt_publish(params=params)
    time.sleep(1)
    params['console']['send_string'] = 'cat /tmp/mqtt/mqtt.log'
    params['console']['wait'] = 1
    params = console_send(params=params)
    # print(params['console']['echo_string'])
    if 'SIGSEGV' in params['console']['echo_string']:
        empty_payload_pass = False
    while True:
        params['console']['send_string'] = 'ps | grep mqtt'
        params['console']['wait'] = 1
        params = console_send(params=params)
        # print(params['console']['echo_string'])
        if 'mqtt.elf' not in params['console']['echo_string']:
            params['console']['send_string'] = '/etc/init.d/mqtt restart'
            params['console']['wait'] = 1
            params = console_send(params=params)
        else:
            break
    print(topic, '的空载攻击通过:', empty_payload_pass)
    return topic, empty_payload_pass, params


def cmd_injection_test(params):
    cmd_dict = topics[t_pre][t_pos]
    i_list = walk_cmd_dict(cmd_dict=cmd_dict)
    cmd_injection_pass = {}
    for k in range(len(i_list)):
        cmd_dict_copy = copy.deepcopy(cmd_dict)
        set_cmd_dict(cmd_dict=cmd_dict_copy, index_list=i_list[k], value='flagthn')
        for payload in payloads_:
            cmd_str = json.dumps(cmd_dict_copy)
            cmd_str = cmd_str.replace('flagthn', payload)
            injected_filename = "_".join(
                [
                    "injected",
                    datetime.datetime.now().strftime("%H%M%S"),
                    ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
                ]
            )
            cmd_injection_pass[cmd_str] = {
                'filename': injected_filename,
                'result': 'unknown'
            }
            cmd_str = cmd_str.replace('占位符', injected_filename)
            params['mqtt']['payload'] = cmd_str
            params = mqtt_publish(params=params)
            print(t, '\n', cmd_str, '\n', 'Done', '\n', '\n')
            time.sleep(0.5)
    return cmd_injection_pass


def cmd_injection_check(params):
    params['console']['send_string'] = 'find / -iname "*injected*"'
    params['console']['format'] = 'str'
    params['console']['wait'] = 10
    params = console_send(params=params)
    for topic in results.keys():
        result = results[topic]
        cmd_injection_pass = result['cmd_injection']
        if cmd_injection_pass is not None:
            for cmd_str in cmd_injection_pass.keys():
                if cmd_injection_pass[cmd_str]['filename'] in params['console']['echo_string']:
                    cmd_injection_pass[cmd_str]['result'] = 'fail'
                else:
                    cmd_injection_pass[cmd_str]['result'] = 'pass'
    return results


if __name__ == '__main__':
    ip = '192.168.1.1'
    ssh_pass = '68be6a1e3d451fab'
    master_model = 'EW3000GX-PRO'
    slave_model = 'H30M'
    salve_sn = 'G1SK4AT00061B'
    results = {}
    payloads_ = read_payloads()
    params_ = None
    for t_pre in topics.keys():
        for t_pos in topics[t_pre].keys():
            t, result_ep, params_ = empty_payload_test(ip, ssh_pass, t_pre, t_pos)
            result_t = {'empty_payload': result_ep}
            if topics[t_pre][t_pos] is not None:
                result_ci = cmd_injection_test(params_)
                result_t['cmd_injection'] = result_ci
            else:
                result_t['cmd_injection'] = None
            results[t] = result_t
    # 打开文件并使用 pickle 保存字典
    with open('reports/{} MQTT空载&注入测试.pkl'.format(master_model), 'wb') as f:
        pickle.dump(obj=results, file=f)
    results = cmd_injection_check(params=params_)
    # 打开文件并使用 pickle 保存字典
    with open('reports/{} MQTT空载&注入测试.pkl'.format(master_model), 'wb') as f:
        pickle.dump(obj=results, file=f)
    # ip = '192.168.1.1'
    # ssh_pass = '68be6a1e3d451fab'
    # master_model = 'EW3000GX-PRO'
    # slave_model = 'H30M'
    # salve_sn = 'G1SK4AT00061B'

    lines = [
        'MQTT Broker IP: {}'.format(ip),
        '主设备型号: {}'.format(master_model),
        '从设备型号: {}'.format(slave_model),
        '从设备序列号: {}'.format(salve_sn),
        '==========================================='
    ]
    conclusion_ep = True
    conclusion_ci = True
    for t in results.keys():
        lines.append('topic: {}'.format(t))
        lines.append('空载荷有处理: {}'.format(results[t]['empty_payload']))
        if not results[t]['empty_payload']:
            conclusion_ep = False
        lines.append('===========================================')
        if results[t]['cmd_injection'] is not None:
            lines.append('命令注入测试:')
            results_ci = results[t]['cmd_injection']
            for cmd_str in results_ci.keys():
                lines.append('注入载荷:\n{}'.format(cmd_str))
                lines.append('检查生成文件: {}'.format(results_ci[cmd_str]['filename']))
                lines.append('检查结果: {}'.format(results_ci[cmd_str]['result']))
                if results_ci[cmd_str]['result'] != 'pass':
                    conclusion_ci = False
                lines.append('===========================================')
    conclusion = conclusion_ep and conclusion_ci
    conclusion_text = {True: '通过', False: '不通过'}
    lines.append('结论: {}'.format(conclusion_text[conclusion]))
    if not conclusion:
        lines.append(
            '原因: 空载荷测试{}，命令注入{}'.format(
                conclusion_text[conclusion_ep], conclusion_text[conclusion_ci]
            )
        )
    lines='\n'.join(lines)
    with open('reports/{} MQTT空载&注入测试.txt'.format(master_model), 'w') as f:
        f.writelines(lines)
    print('Done')
