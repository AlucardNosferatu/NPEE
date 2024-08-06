import time

import pywifi as pywifi
from pywifi import const


def wifi_connect(params):
    """
    连接WiFi
    """
    print_("开始连接WiFi", params)
    misc_params = params['misc']
    # wifi_excluded_iface = misc_params['wifi_excluded_iface']
    wifi_target_ssid = misc_params['wifi_target_ssid']
    if 'wifi_try_connect' in misc_params.keys():
        wifi_try_connect = misc_params['wifi_try_connect']
    else:
        wifi_try_connect = 5
    if 'wifi_try_wait' in misc_params.keys():
        wifi_try_wait = misc_params['wifi_try_wait']
    else:
        wifi_try_wait = 3
    wifi = pywifi.PyWiFi()
    print_("WiFi接口已初始化", params)
    misc_params['wifi_result'] = [False, None]
    for iface in wifi.interfaces():
        # if wifi_excluded_iface is not None:
        #     if iface == wifi_excluded_iface:
        #         print('网卡:{}已连接，跳过'.format(iface.name()))
        #         continue
        print_('使用网卡:{}进行连接'.format(iface.name()), params)
        iface.disconnect()
        time.sleep(1)
        try_scan = 5
        scan_res = []
        while 0 < try_scan:
            iface.scan()
            time.sleep(10)
            scan_res = iface.scan_results()
            try_scan -= 1
            if len(scan_res) > 0:
                print_("这个网卡搜到的SSID数量: %s" % len(scan_res), params)
                print_("| %s |  %s |  %s | %s" % ("WIFI_ID", "SSID", "BSSID", "signal"), params)
                exist_target = None
                for index, wifi_info in enumerate(scan_res):
                    try:
                        print_(
                            "| {} | {} | {} | {} \n".format(index, wifi_info.ssid, wifi_info.bssid, wifi_info.signal),
                            params
                        )
                    except BaseException as e:
                        print_('列出SSID时发生错误:{}'.format(repr(e)), params)
                    if wifi_info.ssid == wifi_target_ssid:
                        if exist_target is None:
                            exist_target = wifi_info
                        else:
                            print_(
                                '警告：出现多个相同SSID的WiFi信号，优先选择先发现的信号：\nSSID:{} BSSID:{}'.format(
                                    exist_target.ssid, exist_target.bssid
                                ),
                                params
                            )
                if exist_target is not None:
                    connected_target = False
                    try_connect = wifi_try_connect
                    while not connected_target and try_connect > 0:
                        iface.connect(exist_target)
                        try_connect -= 1
                        try_wait = wifi_try_wait
                        while try_wait > 0:
                            time.sleep(5)
                            try_wait -= 1
                            if iface.status() == const.IFACE_CONNECTED:
                                connected_target = True
                                print_('WiFi连接SSID:{}成功'.format(wifi_target_ssid), params)
                                break
                            else:
                                print_(
                                    'WiFi连接SSID:{}失败，剩余等待5s次数:{}，重试次数:{}'.format(
                                        wifi_target_ssid, try_wait, try_connect
                                    ),
                                    params
                                )
                    if connected_target:
                        misc_params['wifi_result'] = [True, iface]
                        return params
                    else:
                        print_("这个网卡连不上目标，再试一次！剩余重试次数:{}".format(try_scan), params)
                else:
                    print_("这个网卡没搜到目标，再试一次！剩余重试次数:{}".format(try_scan), params)
            else:
                print_("这个网卡啥也没搜到，再试一次！剩余重试次数:{}".format(try_scan), params)
        print_("这个网卡啥也没搜到，换张网卡", params)
    print_("每张网卡都试过去了，还是不行！", params)
    return params


def print_(info_str, params):
    if 'log' in params.keys() and 'logger' in params['log'].keys():
        logger = params['log']['logger']
        logger.info(info_str)
    else:
        print(info_str)
