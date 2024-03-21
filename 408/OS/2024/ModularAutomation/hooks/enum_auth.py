
def h0(params):
    params['wvt']['injected_cmd'] = {
        "password": "U2FsdGVkX18jTvtRhxDBCEHUDhFsPcNWnPcJTbELjrZLmwn3A/wO1cTtlL+5q+BO",
        "username": "admin",
        "time": "1711012089",
        "encry": True,
        "limit": False,
        "setInit": False
    }
    params['wvt']['injected_api'] = '/cgi-bin/luci/api/auth'
    params['wvt']['inject_method'] = 'login'
    return params
