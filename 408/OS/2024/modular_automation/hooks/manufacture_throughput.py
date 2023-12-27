import datetime
import time

time_format = "%Y年%m月%d日-%H时%M分%S秒"
dut_ip = '192.168.110.1'
wired_ep = '192.168.110.10'
wireless_ep = '192.168.110.24'
ssid = '@EW1200GPro-2G'
ssid_5g = '@EW1200GPro-5G'
ssid_config = [
    "uci set sysinfo.@sysinfo[0].forwardMode='AP'",
    "uci set wireless.MT7615D_1_1.bw='80'",
    "uci set wireless.MT7615D_1_2.bw='20'",
    "uci set wireless.MT7615D_1_1.channel='36'",
    "uci set wireless.MT7615D_1_2.channel='1'",
    f"uci set wireless.ra0.ssid='{ssid_5g}'",
    f"uci set wireless.rax0.ssid='{ssid}'",
    "uci commit wireless",
    "wifi",
    "killall factory",
    "echo OK"
]


def h0(params):
    params['mt_queue'] = [
        {
            'task_label': '2.4G_TX', 'SSID': ssid, 'chariot_duration': 15,
            'ep_pair': {
                'ep1': wired_ep, 'ep2': wireless_ep, 'flows_per_pair': 10, 'script': 'Throughput',
                'protocol': 'TCP',
                'rate_limit': 'unlimited', 'group_name': 'autotest'
            }
        },
        {
            'task_label': '2.4G_TX', 'SSID': ssid, 'chariot_duration': 15,
            'ep_pair': {
                'ep1': wireless_ep, 'ep2': wired_ep, 'flows_per_pair': 10, 'script': 'Throughput',
                'protocol': 'TCP',
                'rate_limit': 'unlimited', 'group_name': 'autotest'
            }
        },
        {
            'task_label': '5G_RX', 'SSID': ssid_5g, 'chariot_duration': 15,
            'ep_pair': {
                'ep1': wired_ep, 'ep2': wireless_ep, 'flows_per_pair': 10, 'script': 'Throughput',
                'protocol': 'TCP',
                'rate_limit': 'unlimited', 'group_name': 'autotest'
            }
        },
        {
            'task_label': '5G_RX', 'SSID': ssid_5g, 'chariot_duration': 15,
            'ep_pair': {
                'ep1': wireless_ep, 'ep2': wired_ep, 'flows_per_pair': 10, 'script': 'Throughput',
                'protocol': 'TCP',
                'rate_limit': 'unlimited', 'group_name': 'autotest'
            }
        }
    ]
    params = h18(params=params)
    return params


def h1(params):
    misc_params = params['misc']
    ping_result = misc_params['ping_result']
    logger = params['log']['logger']
    logger.debug('PING测试结果:{}'.format(ping_result[1]))
    params['if_switch'] = ping_result[0]
    return params


def h2(params):
    time.sleep(0.5)
    return params


def h3(params):
    time.sleep(5)
    return params


def h4(params):
    return params


def h5(params):
    logger = params['log']['logger']
    logger.debug('控制台回显:{}'.format(params['console']['echo_string']))
    params['mt_params'] = params['mt_queue'].pop(0)
    misc_params = params['misc']
    misc_params['wifi_target_ssid'] = params['mt_params']['SSID']
    logger.debug('此次要连接WiFi的SSID:{}'.format(misc_params['wifi_target_ssid']))
    return params


def h6(params):
    params['chariot']['duration'] = params['mt_params']['chariot_duration']
    logger = params['log']['logger']
    logger.debug('打流时长设置为:{}'.format(params['chariot']['duration']))
    return params


def h7(params):
    params['chariot']['pairs'] = [params['mt_params']['ep_pair']]
    logger = params['log']['logger']
    for pair in params['chariot']['pairs']:
        # pair = {
        #     'ep1': '',  # 必填
        #     'ep2': '',  # 必填
        #     'flows_per_pair': 1,  # 可选
        #     'script': 'Throughput',  # 可选
        #     'protocol': 'TCP',  # 可选
        #     'rate_limit': 'unlimited',  # 可选
        #     'group_name': 'autotest'  # 可选
        # }
        logger.debug('打流对配置:')
        logger.debug('#发送端IP:{}'.format(pair['ep1']))
        logger.debug('#接收端IP:{}'.format(pair['ep2']))
        logger.debug('#脚本名称:{}'.format(pair['script']))
        logger.debug('#使用协议:{}'.format(pair['protocol']))
        logger.debug('#速率限制:{}'.format(pair['rate_limit']))
        logger.debug('#组名:{}'.format(pair['group_name']))
    return params


def h8(params):
    params['chariot']['timeout'] = 5
    logger = params['log']['logger']
    logger.debug('打流结束超时:{}'.format(params['chariot']['timeout']))
    return params


def h9(params):
    thr_data = params['chariot']['thr_data']
    if 'mt_results' not in params.keys():
        params['mt_results'] = []
    params['mt_results'].append(thr_data)
    logger = params['log']['logger']
    logger.debug('本轮打流平均吞吐量:'.format(thr_data["total_throughput"]))
    if len(params['mt_queue']) > 0:
        logger.debug('继续下一轮打流（每次测试4轮，还剩{}轮）'.format(len(params['mt_queue'])))
        params['if_switch'] = False
    else:
        logger.debug('完成4轮打流，本次测试结束，记录数据')
        params['if_switch'] = True
    return params


def h10(params):
    params['console']['send_string'] = 'reboot'
    params['console']['format'] = 'str'
    params['console']['wait'] = 2
    logger = params['log']['logger']
    logger.debug('准备重启设备')
    return params


def h11(params):
    if 'mt' not in params.keys():
        params['mt'] = {}
    params['mt']['template_path'] = 'reports/template_mt.xlsx'
    params['mt']['save_path'] = 'reports/产测吞吐.xlsx'
    params = read_template_mt(params=params)
    logger = params['log']['logger']
    logger.debug('准备读取报告模板:{}'.format(params['mt']['template_path']))
    logger.debug('准备保存的文件名:{}'.format(params['mt']['save_path']))
    return params


def h12(params):
    if 'tx_history' not in params.keys():
        params['tx_history'] = []
    if 'rx_history' not in params.keys():
        params['rx_history'] = []
    if 'tx_5g_history' not in params.keys():
        params['tx_5g_history'] = []
    if 'rx_5g_history' not in params.keys():
        params['rx_5g_history'] = []
    if 'timestamp_history' not in params.keys():
        params['timestamp_history'] = []

    params['tx_history'].append(params['mt_results'][0]['total_throughput'])
    params['rx_history'].append(params['mt_results'][1]['total_throughput'])
    params['tx_5g_history'].append(params['mt_results'][2]['total_throughput'])
    params['rx_5g_history'].append(params['mt_results'][3]['total_throughput'])
    params['timestamp_history'].append(datetime.datetime.now().strftime(time_format))
    params['mt_results'].clear()

    data_src_dict = {
        'tx_history': params['tx_history'],
        'rx_history': params['rx_history'],
        'tx_5g_history': params['tx_5g_history'],
        'rx_5g_history': params['rx_5g_history'],
        'timestamp_history': params['timestamp_history']
    }
    params['excel']['data_src_dict'] = data_src_dict
    params['excel']['save_path'] = params['mt']['save_path']
    logger = params['log']['logger']
    logger.debug('准备保存报告')
    return params


def h13(params):
    console_params = params['console']
    logger = params['log']['logger']
    if console_params['exception'] is None:
        logger.info('控制台动作正常完成')
        params['if_switch'] = False
    else:
        logger.error('控制台动作出现异常:{}'.format(console_params['exception']))
        params['if_switch'] = True
    return params


def h14(params):
    misc_params = params['misc']
    wifi_result = misc_params['wifi_result']
    params['if_switch'] = wifi_result[0]
    logger = params['log']['logger']
    logger.debug('WiFi成功连接？{}'.format(wifi_result[0]))
    return params


def h15(params):
    time.sleep(30)
    params['console']['send_string'] = 'uci show sysinfo'
    params['console']['format'] = 'str'
    params['console']['wait'] = 10
    return params


def h16(params):
    echo_string = params['console']['echo_string']
    if "forwardMode='AP'" in echo_string:
        params['if_switch'] = True
    else:
        params['if_switch'] = False
    return params


def h17(params):
    chariot_params = params['chariot']
    logger = params['log']['logger']
    if chariot_params['exception'] is None:
        logger.info('打流动作正常完成')
        params['if_switch'] = False
    else:
        logger.error('打流动作出现异常:{}'.format(chariot_params['exception']))
        params['if_switch'] = True
        params['mt_queue']: list
        params['mt_queue'].insert(0, params['mt_params'])
    return params


def h18(params):
    params['console'] = {'console_type': 'ssh', 'dut_ip': dut_ip, 'ssh_pass': 'ruijie@ap#ykhwzx!'}
    params['console']['send_string'] = ' && '.join(ssid_config)
    params['console']['format'] = 'str'
    params['console']['wait'] = 10
    params['misc'] = {'ping_host': dut_ip, 'ping_times': 1}
    params['chariot'] = {}
    logger = params['log']['logger']
    logger.info('任务参数已全部装订')
    logger.debug('设备WAN口IP:{}'.format(dut_ip))
    logger.debug('有线网卡IP:{}'.format(wired_ep))
    logger.debug('无线网卡IP:{}'.format(wireless_ep))
    logger.debug('2.4G WiFi SSID:{} 5G WiFi SSID:{}'.format(ssid, ssid_5g))
    return params


def read_template_mt(params):
    mt_params = params['mt']
    template_path = mt_params['template_path']
    if 'excel' not in params.keys():
        params['excel'] = {}
    params['excel']['template_path'] = template_path
    return params


def read_testcases_mt(params):
    mt_params = params['mt']
    testcase_path = mt_params['testcase_path']
    params['excel']['testcase_path'] = testcase_path
    return params
