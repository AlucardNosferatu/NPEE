from __future__ import annotations

import json
import uuid

from flask import Flask, request, Response
from flask_cors import CORS

from core.scheduler_fcfs import create_waiting_task, kill_running_task, suspend_or_resume

flask_app = Flask(__name__)
CORS(flask_app)


def resp_wrapper(ret: bool, msg: str | list | dict):
    resp = json.dumps({'code': 0, 'message': {True: '成功', False: '失败'}[ret], 'data': msg})
    resp = Response(response=resp, status=200, content_type='application/json; charset=utf-8')
    return resp


@flask_app.route('/create_task', methods=['POST'])
def create_task():
    if request.method == 'POST':
        data = json.loads(request.data.decode())
        # params = dict(request.args)
        # print(data)
        # print(params)
        task_id = str(uuid.uuid4())
        task = [task_id] + data['task_params_list']
        # data['task_params_list'] = ['task_hook.py', 'task_map.pos', ['ZAP', 'WINDOWS_UI'], None]
        create_waiting_task(task=task)
        resp = resp_wrapper(ret=True, msg={'task_id': task_id})
        return resp


@flask_app.route('/abort_task', methods=['POST'])
def abort_task():
    if request.method == 'POST':
        data = json.loads(request.data.decode())
        # params = dict(request.args)
        # print(data)
        # print(params)
        r_task_id = data['r_task_id']
        exists = kill_running_task(r_task_id=r_task_id)
        resp = resp_wrapper(ret=True, msg={'exists': exists})
        return resp


@flask_app.route('/suspend_task', methods=['POST'])
def suspend_task():
    if request.method == 'POST':
        data = json.loads(request.data.decode())
        # params = dict(request.args)
        # print(data)
        # print(params)
        task_id = data['task_id']
        suspend = data['suspend']
        exists = suspend_or_resume(task_id=task_id, suspend=suspend)
        resp = resp_wrapper(ret=True, msg={'exists': exists})
        return resp


if __name__ == '__main__':
    print('Done')
