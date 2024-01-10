import pyvisa


def ps_init(params):
    ps_params = params['ps']
    res_name = ps_params['res_name']
    baud_rate = ps_params['baud_rate']
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
        code = ps_instr.write('SOUR:VOLT {}'.format(volt))
        ps_params['code'] = code
        ps_params['exception'] = None
    except Exception as e:
        ps_params['code'] = None
        ps_params['exception'] = e
    return params
