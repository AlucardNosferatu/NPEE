import inspect


def task_a(a):
    print('line 1')
    # line2
    print('line 2, a={}'.format(a))
    a += 1
    print('line 3')
    # cond = a < 1000
    # jmp line2
    print(a)


def exec_task(params, func, flag, _pause):
    _ = params
    flag.clear()
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
            if index >= 0:
                if exec_line is not None:
                    exec(exec_line)
            else:
                break
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


if __name__ == '__main__':
    exec_task({'a': 0}, task_a, [], [False])
