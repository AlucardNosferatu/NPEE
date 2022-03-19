import json
import threading
import time
import uuid

from flask import request

from FlowControl.MediaAgent import sr_interaction, app


class Sender:
    window_size = None
    frame_cursor = None
    window_cursor = None
    frame_queue = None

    timer_thread = None
    timer_table = None
    timer_active = None
    timer_reset = None
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
        self.timer_thread = threading.Thread(target=self.alive_timer)
        self.timer_thread.start()

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

    def recv_com(self, com_str):
        if com_str == 'send':
            self.send_new()
        elif com_str.startswith('resend_'):
            self.resend_old(int(com_str.split('_')[0]))

    def alive_timer(self):
        self.timer_table = []
        self.timer_active = []
        self.timer_reset = []
        for i in range(0, self.window_size):
            self.timer_table.append(0)
            self.timer_active.append(False)
            self.timer_reset.append(True)
        while True:
            time.sleep(0.1)
            for i in range(0, self.window_size):
                if self.timer_reset[i]:
                    print('timer has been reset')
                    self.timer_table[i] = 0
                    self.timer_reset[i] = False
                if self.timer_active[i]:
                    self.timer_table[i] += 1
                    if self.timer_table[i] % 10 == 0:
                        print('timer ' + str(i) + ':', self.timer_table[i])
                if self.timer_table[i] > 10 * self.time_out:
                    print('timeout, resend old frame')
                    self.resend_old(i)


sender_inst = None


@app.route("/recv", methods=['POST'])
def recv():
    if request.method == "POST":
        c_da = request.data
        data = json.loads(c_da.decode())

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
