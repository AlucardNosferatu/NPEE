def h0(params):
    return params


def h1(params):
    chariot_params = params['chariot']
    logger = params['log']['logger']
    if chariot_params['exception'] is None:
        logger.info('打流动作正常完成')
        params['if_switch'] = False
    else:
        logger.error('打流动作出现异常:{}'.format(chariot_params['exception']))
        params['if_switch'] = True
    return params


def h2(params):
    chariot_params = params['chariot']
    del chariot_params['ic_api']
    return params


def h3(params):
    params['database'] = {}
    params['database']['db_type'] = 'redis'
    params['database']['db_ip'] = '127.0.0.1'
    params['database']['db_port'] = 6379
    params['database']['db_index'] = 0
    params['database']['db_pass'] = 'ruijie@redis'
    params['database']['key'] = 'chariot'
    params['database']['value'] = params['chariot']['thr_data']
    return params


def h4(params):
    params['if_switch'] = params['database']['exists']
    return params


def h5(params):
    params = h0(params=params)
    return params
