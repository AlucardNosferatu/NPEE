import inspect
from threading import Thread
import time


def task_a(var1, var2, var3, ret):
    _pause = _pause
    # fuck
    var1 += var2
    # jmp fuck
    var2 += var3
    ret.append(var1)
    print('var1:{}'.format(var1))
    # cond = var1 < 1000
    exec_task({'var1': var1, 'var2': var2, 'var3': var3, 'ret': ret}, task_a, [], _pause)


def exec_task(params, func, flag, _pause):
    _ = params
    flag.clear()
    lines = list(inspect.getsourcelines(func)[0])
    lines.pop(0)
    args = inspect.getfullargspec(func)
    keys = args.args
    for key in keys:
        exec("{}=params['{}']".format(key, key))
    lines_ = lines.copy()
    while len(lines_) > 0:
        cond = True
        line = lines.pop(0).strip()
        if line.startswith('# cond'):
            line = line[1:].strip()
            # print('条件:{}'.format(line))
            exec(line)
            line = lines.pop(0).strip()
        wait = False
        while _pause[0]:
            if not wait:
                print('pause')
                wait = True
        if wait:
            print('resume')
        if cond:
            exec(line)
        time.sleep(0.01)
    flag.append(True)


if __name__ == '__main__':
    ret = []
    flag = []
    pause = [False]
    fb_thread = Thread(target=exec_task, args=({'var1': 1, 'var2': 2, 'var3': 3, 'ret': ret}, task_a, flag, pause))
    fb_thread.start()
    while len(flag) <= 0 or not flag[0]:
        time.sleep(0.1)
        pause[0] = True
        time.sleep(2)
        print('返回值:{}'.format(ret))
        pause[0] = False
