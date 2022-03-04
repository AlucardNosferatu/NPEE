import json
import threading
import time

import requests as requests
from flask import Flask, request
import uuid

app = Flask(__name__)
send_stack = {'max_order': 1, 'next_order': -1, 'ack_order': -1, 'resend_cache': ''}
recv_stack = {'max_order': 1, 'next_order': -1}
time_out = 5
ack_delay = 2
send_delay = 2


def sr_interaction(url, req_dict):
    server_url = 'http://127.0.0.1:20291'
    server_url += url
    headers = {
        "Content-Type": "application/json; charset=UTF-8"
    }
    json_dict = json.dumps(req_dict)
    response = requests.post(server_url, data=json_dict, headers=headers)
    result = None
    if response is not None:
        response.raise_for_status()
        result = json.loads(response.content.decode('utf-8'))
    return result


def resend_after_timeout():
    sr_interaction(
        '/send',
        {'ack_order': -1}
    )


def send_new_frame(ss):
    content = str(uuid.uuid4())
    sr_interaction(
        '/recv',
        {'content': content, 'order': ss['next_order']}
    )
    ss['ack_order'] = ss['next_order']
    ss['resend_cache'] = content
    ss['next_order'] += 1
    if ss['next_order'] > ss['max_order']:
        ss['next_order'] = 0


def send_old_frame(ss):
    sr_interaction(
        '/recv',
        {'content': ss['resend_cache'],
         'order': ss['ack_order']}
    )


@app.route("/send", methods=['POST'])
def send():
    global send_stack
    if send_stack['next_order'] == -1:
        send_stack['next_order'] = 0
    if send_stack['ack_order'] == -1:
        send_stack['ack_order'] = 0
    if request.method == "POST":
        c_da = request.data
        data = json.loads(c_da.decode())
        if 'start' in data:
            # send_new_frame(send_stack)
            timer_snf = threading.Timer(send_delay, send_new_frame, (send_stack,))
            timer_snf.start()
        elif 'ack_order' in data:
            print('need ack', send_stack['ack_order'], 'get ack', data['ack_order'])
            if data['ack_order'] == send_stack['ack_order']:
                timer_snf = threading.Timer(send_delay, send_new_frame, (send_stack,))
                timer_snf.start()
            else:
                timer_sof = threading.Timer(send_delay, send_old_frame, (send_stack,))
                timer_sof.start()
        else:
            pass
        return json.dumps(
            {
                '经典的错误': '标注的零分'
            },
            ensure_ascii=False
        )


def ack_thread(rs):
    sr_interaction(
        '/send',
        {'ack_order': rs['next_order']}
    )
    rs['next_order'] += 1
    if rs['next_order'] > rs['max_order']:
        rs['next_order'] = 0


@app.route("/recv", methods=['POST'])
def recv():
    global recv_stack
    if recv_stack['next_order'] == -1:
        recv_stack['next_order'] = 0
    if request.method == "POST":
        c_da = request.data
        data = json.loads(c_da.decode())
        if 'order' in data:
            if data['order'] == recv_stack['next_order']:
                print(data['order'], data['content'])
                timer_ack = threading.Timer(time_out, ack_thread, (recv_stack,))
                timer_ack.start()
            else:
                pass
        else:
            pass
        return json.dumps(
            {
                '经典的错误': '标注的零分'
            },
            ensure_ascii=False
        )


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("20291"),
        debug=True, threaded=True
    )
