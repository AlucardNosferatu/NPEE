import json
import os
import subprocess
import threading
import time

from flask import Flask, request, Response
from flask_cors import CORS

flask_app = Flask(__name__)
CORS(flask_app)

params = {}
keepalive = 0
period = 60
pid = ''
# worker_script = 'power_cycle_worker.py'
worker_exe = 'power_cycle_worker.exe'


# 自定义序列化函数
def custom_serializer(obj):
    try:
        obj_str = json.dumps(obj=obj)
        return obj_str
    except Exception as e:
        print(repr(e))
        return 'CANNOT_SERIALIZE'


def resp_wrapper(ret: bool, msg: str | list | dict):
    resp = json.dumps(
        obj={'code': 0, 'message': {True: '成功', False: '失败'}[ret], 'data': msg},
        default=custom_serializer
    )
    resp = Response(response=resp, status=200,
                    content_type='application/json; charset=utf-8')
    return resp


@flask_app.route('/assign_worker', methods=['GET'])  # type: ignore
def assign_worker():
    if request.method == 'GET':
        resp = resp_wrapper(ret=True, msg={'params': params})
        return resp


@flask_app.route('/report_result', methods=['POST'])  # type: ignore
def report_result():
    global params, keepalive, pid
    if request.method == 'POST':
        keepalive = 0
        data = json.loads(request.data.decode())
        params = data['params']
        pid = data['pid']
        resp = resp_wrapper(ret=True, msg={'params': params})
        return resp


def watchdog():
    global keepalive, pid
    while True:
        time.sleep(1)
        keepalive += 1
        print('###watchdog counter:{}###'.format(keepalive))
        if keepalive > period:
            kill_worker()
            start_worker()
            keepalive = 0


def start_server():
    w_thread = threading.Thread(target=watchdog)
    w_thread.start()
    start_worker()
    flask_app.run(
        host='0.0.0.0',
        port=20291,
        debug=False,
        threaded=True
    )


def start_worker():
    try:
        subprocess.Popen(
            # ['python', worker_exe],
            [worker_exe],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        print(f"已启动独立进程运行 {worker_exe}")
    except FileNotFoundError:
        print(f"找不到指定的脚本文件: {worker_exe}")
    except Exception as e:
        print(f"启动进程时出现错误: {e}")


def kill_worker():
    global pid
    try:
        os.kill(int(pid), 9)  # 发送 SIGKILL 信号给指定 PID 进程
        print(f"进程 {pid} 已被成功终止")
    except ProcessLookupError:
        print(f"进程 {pid} 不存在")
    except PermissionError:
        print(f"没有权限终止进程 {pid}")
    except Exception as e:
        print(f"其它类型的错误: {repr(e)}")
        print(f"pid: {pid}")
    pid = ''


if __name__ == '__main__':
    params_from_json = json.loads(
        s='\n'.join(
            open(
                file='reports/power_cycle.json',
                mode='r', encoding='utf-8'
            ).readlines()
        )
    )
    period = params_from_json['daemon']['period']
    worker_exe = params_from_json['daemon']['worker_exe']
    params = {
        'error_texts': params_from_json['error_texts'],
        'ps': {
            'res_name': params_from_json['pcr']['res_name'],
            'baud_rate': params_from_json['pcr']['baud_rate'],
            'acdc': 'ac',
            'freq': params_from_json['pcr']['freq'],
            'range': params_from_json['pcr']['range'],
            'debug': params_from_json['pcr']['debug']
        },
        'excel': {
            'template_path': 'reports/template_pc.xlsx'
        },
        'misc': {
            'ping_host': params_from_json['dut']['lan_ip'],
            'ping_times': params_from_json['dut']['ping_times']
        }
    }
    testcase_template = {
        'volt': 220, 'ton': 1, 'toff': 1, 'tgap': 1, 'max_tboot': 120,
        'max_tcheck': 60, 'max_tcheck_5g': 60, 'ssid': params_from_json['dut']['ssid'],
        'ssid_5g': params_from_json['dut']['ssid_5g'],
        'wait_after_boot': params_from_json['test']['wait_after_boot'],
        'sim_test': params_from_json['dut']['sim_test'],
        'console_port': params_from_json['dut']['port'], 'console_baud_rate': params_from_json['dut']['baud_rate'],
        'switch_port': params_from_json['switch']['port'], 'switch_baud_rate': params_from_json['switch']['baud_rate'],
        'console_password': params_from_json['dut']['console_password'],
        'boot_count': 0, 'boot_ok': False, 'tboot': -1.0, 'tcheck': -1.0, 'tcheck_5g': '',
        'wifi_ok': False, 'wifi_5g_ok': '', 'ping_ok': False, 'ping_5g_ok': '', 'sim_ok': ''
    }
    volt_combo = params_from_json['test']['volt_combo']
    ton_combo = params_from_json['test']['ton_combo']
    toff_combo = params_from_json['test']['toff_combo']
    tboot_combo = params_from_json['test']['tboot_combo']
    tcheck_combo = params_from_json['test']['tcheck_combo']
    tcheck_5g_combo = params_from_json['test']['tcheck_5g_combo']
    tgap_combo = params_from_json['test']['tgap_combo']
    repeat = params_from_json['test']['repeat']
    params['pc_testcases'] = []
    for volt in volt_combo:
        for ton in ton_combo:
            for toff in toff_combo:
                for tboot in tboot_combo:
                    for tcheck in tcheck_combo:
                        for tcheck_5g in tcheck_5g_combo:
                            for tgap in tgap_combo:
                                for _ in range(repeat):
                                    testcase = testcase_template.copy()
                                    testcase['volt'] = volt
                                    testcase['ton'] = ton
                                    testcase['toff'] = toff
                                    testcase['max_tboot'] = tboot
                                    testcase['max_tcheck'] = tcheck
                                    testcase['max_tcheck_5g'] = tcheck_5g
                                    testcase['tgap'] = tgap
                                    params['pc_testcases'].append(testcase)
    params['pc_report_savepath'] = params_from_json['pc_report_savepath']
    params['webhook'] = {
        'webhook_url': params_from_json['webhook_url'],
        'send_string': '电源切变循环测试已完成'
    }
    start_server()
