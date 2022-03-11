import json
import threading

from flask import Flask, request

from FlowControl.StopWait import sr_interaction

app = Flask(__name__)

send_delay = 2


@app.route("/forward", methods=['POST'])
def forward():
    if request.method == "POST":
        c_da = request.data
        data = json.loads(c_da.decode())
        # frame = data['data']
        # src = data['src']
        dst = data['dst']
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
    if request.method == "POST":
        return json.dumps(
            {
                '经典的错误': '标注的零分'
            },
            ensure_ascii=False
        )
