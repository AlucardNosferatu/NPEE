def h0(params):
    send_string = ['cd', 'cat /proc/mtd']
    send_string = ' && '.join(send_string)
    params['console']['send_string'] = send_string
    params['console']['format'] = 'str'
    params['console']['wait'] = 5
    return params


def h1(params):
    return params


def h2(params):
    echo_string = params['console']['echo_string']
    echo_string = echo_string.split('\r\n')
    return params
