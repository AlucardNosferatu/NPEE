import json
import threading
import time
import uuid

from flask import request

from FlowControl.MediaAgent import sr_interaction, app

sender_inst = None
recv_need_frame = 0
last_recv_frame = -1


class Sender:
    window_size = None
    frame_cursor = None
    window_cursor = None
    frame_queue = None

    timer_thread = None
    timer_table = None
    timer_active = None
    timer_reset = None
    timer_kill = None
    time_out = None
    send_delay = None

    def __init__(self, window_size=8, frame_queue=None):
        if frame_queue is None:
            frame_queue = []
            for i in range(0, 128):
                content = str(uuid.uuid4())
                frame_queue.append(content)
        self.window_size = window_size
        self.frame_queue = frame_queue
        self.window_cursor = 0
        self.frame_cursor = 0
        self.time_out = 10
        self.send_delay = 2
        self.start_timer()

    def kill_timer(self):
        while self.timer_thread.is_alive():
            self.timer_kill = True
            time.sleep(1)

    def start_timer(self):
        self.timer_thread = threading.Thread(target=self.alive_timer)
        self.timer_thread.start()

    def restart_timer(self):
        self.kill_timer()
        self.start_timer()

    def send_new(self):
        if self.frame_cursor < self.window_size:
            self.resend_old(self.frame_cursor)
            self.frame_cursor += 1
        else:
            print("No new frames in current window!")

    def resend_old(self, old_cursor):
        self.timer_active[old_cursor] = False
        self.timer_reset[old_cursor] = True
        frame_to_send = self.frame_queue[self.window_cursor + old_cursor]
        frame_to_send = {'content': frame_to_send, 'no': old_cursor, }
        frame_to_send = {'data': frame_to_send, 'src': '/send', 'dst': '/recv'}
        timer_rof = threading.Timer(
            self.send_delay,
            sr_interaction,
            (
                "/forward",
                frame_to_send
            )
        )
        timer_rof.start()
        self.timer_active[old_cursor] = True

    def recv_ack(self, ack_frame):
        # Use Cumulative Acknowledgement
        for i in range(0, ack_frame + 1):
            self.window_cursor += 1
            self.frame_cursor -= 1
            self.timer_table.pop(0)
            self.timer_active.pop(0)
            self.timer_reset.pop(0)
            self.timer_table.append(0)
            self.timer_active.append(False)
            self.timer_reset.append(True)
        print('第' + str(ack_frame) + '帧的ACK已收到，滑窗已更新')

    def recv_com(self, com_str):
        if com_str == 'send':
            self.send_new()
        elif com_str.startswith('resend_'):
            self.resend_old(int(com_str.split('_')[0]))

    def alive_timer(self):
        self.timer_kill = False
        self.timer_table = []
        self.timer_active = []
        self.timer_reset = []
        for i in range(0, self.window_size):
            self.timer_table.append(0)
            self.timer_active.append(False)
            self.timer_reset.append(True)
        while not self.timer_kill:
            time.sleep(0.1)
            for i in range(0, self.window_size):
                if self.timer_reset[i]:
                    print('timer ' + str(i) + ' has been reset')
                    self.timer_table[i] = 0
                    self.timer_reset[i] = False
                if self.timer_active[i]:
                    self.timer_table[i] += 1
                    if self.timer_table[i] % 10 == 0:
                        print('timer ' + str(i) + ':', self.timer_table[i])
                if self.timer_table[i] > 10 * self.time_out:
                    print(str(i) + ' timeout, resend old frame')
                    self.resend_old(i)
        print('Timer thread has been killed.')


@app.route("/init", methods=['POST'])
def init():
    global sender_inst
    if request.method == "POST":
        if sender_inst is None:
            sender_inst = Sender()
        return json.dumps(
            {
                'info': '全局Sender对象已初始化。'
            },
            ensure_ascii=False
        )


@app.route("/recv", methods=['POST'])
def recv():
    global recv_need_frame, last_recv_frame
    if request.method == "POST":
        c_da = request.data
        data = json.loads(c_da.decode())
        if 'src' in data and 'data' in data:
            if data['src'] == '/send':
                if int(data['data']['no']) == recv_need_frame:
                    last_recv_frame = recv_need_frame
                    recv_need_frame += 1
                    print(data['data']['content'])
                frame_to_send = {'ack_no': last_recv_frame}
                frame_to_send = {'data': frame_to_send, 'src': '/recv', 'dst': '/send'}
                timer_ack = threading.Timer(
                    2,
                    sr_interaction,
                    (
                        "/forward",
                        frame_to_send
                    )
                )
                timer_ack.start()
                info = '第' + str(data['data']['no']) + '帧的ACK已发送。'
            else:
                info = '未定义其它src的有效响应'
        else:
            info = '格式错误，请指定src和data字段'
        # todo:接收端功能
        return json.dumps(
            {
                'info': info
            },
            ensure_ascii=False
        )


# noinspection PyUnresolvedReferences
@app.route("/send", methods=['POST'])
def send():
    global sender_inst
    if request.method == "POST":
        c_da = request.data
        data = json.loads(c_da.decode())
        if type(sender_inst) is Sender:
            if 'src' in data and 'data' in data:
                if data['src'] == '/ctrl':
                    if 'send_1' in data['data']:
                        sender_inst.send_new()
                    elif 'send_n' in data['data']:
                        n = int(data['data']['send_n'])
                        for i in range(0, min(n, sender_inst.window_size)):
                            time.sleep(1)
                            sender_inst.send_new()
                elif data['src'] == '/recv':
                    if 'ack_no' in data['data']:
                        sender_inst.recv_ack(ack_frame=data['data']['ack_no'])
                info = '你调用了send接口。'
            else:
                info = '格式错误，请指定src和data字段'
        else:
            info = '全局Sender对象未初始化，先对/init进行POST以初始化全局Sender对象！'
        return json.dumps(
            {
                'info': info
            },
            ensure_ascii=False
        )


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("20291"),
        debug=True, threaded=False
    )
