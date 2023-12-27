def top_parse_cpu(params):
    top = params['console']['echo_string']
    cpu = top.split('\r\n')[2]
    while '  ' in cpu:
        cpu = cpu.replace('  ', ' ')
    cpu = cpu.split(' ')
    cpu.pop(0)
    top_cpu = {}
    while len(cpu) > 0:
        val = cpu.pop(0)
        key = cpu.pop(0)
        top_cpu[key] = val
    params['console']['top_cpu'] = top_cpu
    return params
