def h0(params):
    send_string = ['cd', 'cat /proc/mtd']
    send_string = ' && '.join(send_string)
    params['console']['send_string'] = send_string
    params['console']['format'] = 'str'
    params['console']['wait'] = 1
    return params


def h1(params):
    return params


def h2(params):
    echo_string = params['console']['echo_string']
    echo_string = echo_string.split('\r\n')
    while not echo_string[0].startswith('mtd'):
        echo_string.pop(0)
    while 'firmware' not in echo_string[-1] and 'backup' not in echo_string[-1]:
        echo_string.pop(-1)
    flash_size_total = 0
    for part in echo_string:
        print(part)
        part = part.split(' ')[1]
        part = int(part, 16)
        flash_size_total += part
    print(
        'Flash容量:{}(10进制)/{}(16进制)字节'.format(
            flash_size_total, hex(flash_size_total)
        )
    )
    return params
