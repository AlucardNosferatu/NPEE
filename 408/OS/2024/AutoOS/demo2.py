import inspect
from threading import Thread
import time


def task_a(a):
    print('line 1')
    # line2
    print('line 2, a={}'.format(a))
    a += 1
    print('line 3')
    # cond = a < 1000
    # jmp line2
    print(a)
    return a * 1224


def exec_task(params, func, flag, _pause, ret_ptr):
    _ = params
    flag.clear()
    ret_ptr.clear()
    lines = list(inspect.getsourcelines(func)[0])
    lines.pop(0)
    lines = [[None, l] for l in lines]
    args = inspect.getfullargspec(func)
    keys = args.args
    for key in keys:
        exec("{}=params['{}']".format(key, key))
    index = 0
    while True:
        if not _pause[0]:
            index, exec_line = parse_line(index, lines, locals_=locals())
            if exec_line is not None:
                exec(exec_line)
            if index < 0:
                break
    if len(ret_ptr) <= 0:
        ret_ptr.append(None)
    flag.append(True)


def parse_line(index, lines, locals_):
    line = get_line(index, lines)
    exec_line = None
    if line is None:
        return -1, exec_line
    if line.startswith('#'):
        if line.startswith('# cond ='):
            index = condition_do(line, index, locals_)
        elif line.startswith('# jmp '):
            index = jump_to(line, index, lines)
        else:
            index = mark_line(line, index, lines)
    else:
        if line.startswith('return '):
            index = -1
            exec_line = exec_return(line)
        else:
            index += 1
            exec_line = line.strip()
    return index, exec_line


def get_line(index, lines):
    try:
        line = lines[index][1].strip()
    except Exception as e:
        _ = e
        line = None
    return line


def condition_do(line, index, locals_):
    line = line.replace('#', '').strip()
    exec(line, locals_)
    if locals_['cond']:
        index += 1
    else:
        index += 2
    return index


def jump_to(line, index, lines):
    mark = line.replace('# jmp', '').strip()
    index = [l[0] for l in lines].index(mark)
    return index


def mark_line(line, index, lines):
    mark = line.replace('#', '').strip()
    index += 1
    lines[index][0] = mark
    return index


def exec_return(line):
    line = line.replace('return ', 'ret_ptr.append(')
    line = line + ')'
    return line


def fire_task(task, args):
    finished = []
    pause = [False]
    ret_ptr = []
    fb_thread = Thread(target=exec_task, args=(args, task, finished, pause, ret_ptr))
    fb_thread.start()
    return args, finished, pause, ret_ptr


if __name__ == '__main__':
    a, f, p, r = fire_task(args={'a': 0}, task=task_a)
    while len(f) <= 0 or not f[0]:
        time.sleep(0.1)
        p[0] = True
        print(a)
        time.sleep(1)
        p[0] = False
    print(r)
