import pyvisa


def ps_init(params):
    ps_params = params['ps']
    res_name = ps_params['res_name']
    baud_rate = ps_params['baud_rate']
    if 'debug' in ps_params.keys() and ps_params['debug']:
        print('DEBUG模式-资源名称:{}-波特率:{}'.format(res_name, baud_rate))
        ps_instr = None  # type: ignore
    else:
        rm = pyvisa.ResourceManager()
        ps_instr: pyvisa.resources.SerialInstrument = rm.open_resource(
            resource_name=res_name)  # type: ignore
        ps_instr.baud_rate = int(baud_rate)
    ps_params['ps_instr'] = ps_instr
    return params


def ps_reset(params):
    ps_params = params['ps']
    ps_instr = ps_params['ps_instr']
    try:
        if 'debug' in ps_params.keys() and ps_params['debug']:
            print('DEBUG模式-设备重置')
            code = None
        else:
            code = ps_instr.write('*RST')
        ps_params['code'] = code
        ps_params['exception'] = None
    except Exception as e:
        ps_params['code'] = None
        ps_params['exception'] = e
    return params


def ps_acdc(params):
    ps_params = params['ps']
    ps_instr = ps_params['ps_instr']
    acdc = ps_params['acdc']
    try:
        if 'debug' in ps_params.keys() and ps_params['debug']:
            print('DEBUG模式-交直流模式:{}'.format(acdc))
            code = None
        else:
            code = ps_instr.write(
                {
                    'ac': 'OUTP:COUP AC',
                    'dc': 'OUTP:COUP DC'
                }[acdc]
            )
        ps_params['code'] = code
        ps_params['exception'] = None
    except Exception as e:
        ps_params['code'] = None
        ps_params['exception'] = e
    return params


def ps_freq(params):
    ps_params = params['ps']
    ps_instr = ps_params['ps_instr']
    freq = ps_params['freq']
    try:
        if 'debug' in ps_params.keys() and ps_params['debug']:
            print('DEBUG模式-交流输出频率:{}'.format(freq))
            code = None
        else:
            code = ps_instr.write('SOUR:FREQ {}'.format(freq))
        ps_params['code'] = code
        ps_params['exception'] = None
    except Exception as e:
        ps_params['code'] = None
        ps_params['exception'] = e
    return params


def ps_range(params):
    ps_params = params['ps']
    ps_instr = ps_params['ps_instr']
    range_ = ps_params['range']
    try:
        if 'debug' in ps_params.keys() and ps_params['debug']:
            print('DEBUG模式-压限档位:{}'.format(range_))
            code = None
        else:
            code = ps_instr.write('SOUR:VOLT:RANG {}'.format(range_))
        ps_params['code'] = code
        ps_params['exception'] = None
    except Exception as e:
        ps_params['code'] = None
        ps_params['exception'] = e
    return params


def ps_toggle(params):
    ps_params = params['ps']
    ps_instr = ps_params['ps_instr']
    toggle = ps_params['toggle']
    try:
        if 'debug' in ps_params.keys() and ps_params['debug']:
            print('DEBUG模式-开关:{}'.format(toggle))
            code = None
        else:
            code = ps_instr.write(
                {
                    'on': 'OUTPUT:STAT ON',
                    'off': 'OUTPUT:STAT OFF'
                }[toggle]
            )
        ps_params['code'] = code
        ps_params['exception'] = None
    except Exception as e:
        ps_params['code'] = None
        ps_params['exception'] = e
    return params


def ps_volt(params):
    ps_params = params['ps']
    ps_instr = ps_params['ps_instr']
    volt = ps_params['volt']
    try:
        if 'debug' in ps_params.keys() and ps_params['debug']:
            print('DEBUG模式-设置电压:{}'.format(volt))
            code = None
        else:
            code = ps_instr.write('SOUR:VOLT {}'.format(volt))
        ps_params['code'] = code
        ps_params['exception'] = None
    except Exception as e:
        ps_params['code'] = None
        ps_params['exception'] = e
    return params
