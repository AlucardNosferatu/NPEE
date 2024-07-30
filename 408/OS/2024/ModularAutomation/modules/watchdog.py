import json
import os
import subprocess
import threading

from flask import Response, request, Flask
from flask_cors import CORS

from modules.http_api import http_post, http_get

flask_app = Flask(__name__)
CORS(flask_app)
fc_ptr = []


def wake(params):
    fc_wd = params['flowchart']['fc_pool']['看门狗']
    fc_ptr.clear()
    fc_ptr.append(fc_wd)
    wd_params = fc_wd.params_bus['watchdog']
    dr_thread = threading.Thread(target=routine, args=(params,))
    dr_thread.start()
    flask_app.run(
        host='0.0.0.0',
        port=wd_params['port'],
        debug=False,
        threaded=True
    )


@flask_app.route('/watchdog', methods=['GET', 'POST'])  # type: ignore
def watchdog():
    wd_params = fc_ptr[0].params_bus['watchdog']
    if request.method == 'GET':
        resp = resp_wrapper(ret=True, msg={'params': wd_params['watched_params']})
    elif request.method == 'POST':
        data = json.loads(request.data.decode())
        wd_params['pid'] = data['pid']
        wd_params['age'] = 0
        wd_params['watched_params'] = data['params']
        resp = resp_wrapper(ret=True, msg={'params': wd_params['watched_params']})
    else:
        resp = resp_wrapper(ret=False, msg='METHOD NOT IMPLEMENTED:{}'.format(request.method))
    return resp


def resp_wrapper(ret: bool, msg: str | list | dict):
    resp = json.dumps(
        obj={'code': 0, 'message': {True: '成功', False: '失败'}[ret], 'data': msg},
        default=custom_serializer
    )
    resp = Response(response=resp, status=200, content_type='application/json; charset=utf-8')
    return resp


def routine(params):
    fc_wd = params['flowchart']['fc_pool']['看门狗']
    end = False
    while not end:
        end = fc_wd.run_step()


def feed(params):
    wd_params = params['watchdog']
    server_url = 'http://127.0.0.1:{}/watchdog'.format(wd_params['port'])  # 服务端接口地址
    data = json.dumps(obj={'params': params, 'pid': str(os.getpid())}, default=custom_serializer)
    try:
        params_ = {'http': {}}
        params_['http']['url'] = server_url
        params_['http']['data'] = data
        params_ = http_post(params=params_)
        result = params_['http']['response']
        if result.status_code < 300:
            wd_params['exception'] = None
        else:
            wd_params['exception'] = result.status_code
    except BaseException as e:
        wd_params['exception'] = e
    return params


def fetch(params):
    wd_params = params['watchdog']
    server_url = 'http://127.0.0.1:{}/watchdog'.format(wd_params['port'])  # 服务端接口地址
    try:
        params_ = {'http': {}}
        params_['http']['url'] = server_url
        params_ = http_get(params=params_)
        result = params_['http']['response']
        if result.status_code < 300:
            data = result.json()  # 解析 JSON 格式的响应数据
            params = data['data']['params']  # 获取服务端返回的 params 变量
            wd_params = params['watchdog']
            wd_params['exception'] = None
        else:
            wd_params['exception'] = result.status_code
    except BaseException as e:
        wd_params = params['watchdog']
        wd_params['exception'] = e
    return params


def bite(params):
    wd_params = params['watchdog']
    pid = wd_params['pid']
    try:
        os.kill(int(pid), 9)  # 发送 SIGKILL 信号给指定 PID 进程
        print(f"进程 {pid} 已被成功终止")
        wd_params['exception'] = None
        wd_params['pid'] = ''
    except ProcessLookupError:
        err_str = f"进程 {pid} 不存在"
        print(err_str)
        wd_params['exception'] = err_str
    except PermissionError:
        err_str = f"没有权限终止进程 {pid}"
        print(err_str)
        wd_params['exception'] = err_str
    except BaseException as e:
        err_str = f"其它类型的错误: {repr(e)}\npid: {pid}"
        print(err_str)
        wd_params['exception'] = err_str
    return params


def bark(params):
    wd_params = params['watchdog']
    exe_file = wd_params['exe_file']
    try:
        subprocess.Popen(
            # ['python', worker_exe],
            [exe_file],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        print(f"已启动独立进程运行 {exe_file}")
        wd_params['exception'] = None
    except FileNotFoundError:
        err_str = f"找不到指定的脚本文件: {exe_file}"
        print()
        wd_params['exception'] = err_str
    except BaseException as e:
        err_str = f"启动进程时出现错误: {e}"
        print(err_str)
        wd_params['exception'] = err_str
    return params


def digest(params):
    wd_params = params['watchdog']
    wd_params['age'] += 1
    return params


# 自定义序列化函数
def custom_serializer(obj):
    try:
        obj_str = json.dumps(obj=obj)
        return obj_str
    except BaseException as e:
        print(repr(e))
        return 'CANNOT_SERIALIZE'
