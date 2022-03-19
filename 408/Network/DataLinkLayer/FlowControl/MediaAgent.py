import json
import random
import threading

import requests as requests
from flask import Flask, request

app = Flask(__name__)

send_delay = 2
random_slots = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]


@app.route("/forward", methods=['POST'])
def forward():
    if request.method == "POST":
        c_da = request.data
        data = json.loads(c_da.decode())
        # frame = data['data']
        # src = data['src']
        dst = data['dst']
        if random.choice(random_slots) == 0:
            timer_prop = threading.Timer(
                send_delay,
                sr_interaction,
                (
                    dst,
                    data
                )
            )
            timer_prop.start()
        return json.dumps(
            {
                '经典的错误': '标注的零分'
            },
            ensure_ascii=False
        )


@app.route("/setting", methods=['POST'])
def setting():
    global random_slots
    if request.method == "POST":
        c_da = request.data
        data = json.loads(c_da.decode())
        if 'lr' in data:
            loss_rate = data['lr']
            if 0 <= loss_rate <= 1:
                one_count = int(loss_rate * 10)
                zero_count = int((1 - loss_rate) * 10)
                random_slots = [1] * one_count
                random_slots = random_slots + [0] * zero_count

        return json.dumps(
            {
                '经典的错误': '标注的零分'
            },
            ensure_ascii=False
        )


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
