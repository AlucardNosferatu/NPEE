def h0(params):
    params['console'] = {
        'console_type': 'ssh',
        'dut_ip': '192.168.110.1',
        'ssh_pass': '57e541f69676ce62',
        'band_type': '5G',
        'iwpriv_reg': '820d002c'
    }
    return params


def h1(params):
    return params


def h2(params):
    params['console']['send_string'] = 'top -d1'
    params['console']['format'] = 'str'
    params['console']['wait'] = 5
    return params


def h3(params):
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
    wcr_parsed = params['console']['wcr_parsed']
    iwpss_parsed = params['console']['iwpss_parsed']
    iwps_parsed = params['console']['iwps_parsed']
    iwpreg_parsed = params['console']['iwpreg_parsed']

    conclusion = {}
    if wcr_parsed['floornoise'] < -90:
        conclusion['底噪'] = '屏蔽箱:{}dB'.format(wcr_parsed['floornoise'])
    elif wcr_parsed['floornoise'] < -80:
        conclusion['底噪'] = '无干扰:{}dB'.format(wcr_parsed['floornoise'])
    elif wcr_parsed['floornoise'] < -70:
        conclusion['底噪'] = '轻度干扰:{}dB'.format(wcr_parsed['floornoise'])
    elif wcr_parsed['floornoise'] < -60:
        conclusion['底噪'] = '中度干扰:{}dB'.format(wcr_parsed['floornoise'])
    elif wcr_parsed['floornoise'] < -50:
        conclusion['底噪'] = '重度干扰:{}dB'.format(wcr_parsed['floornoise'])
    else:
        conclusion['底噪'] = '极端干扰（可能连不上！）:{}dB'.format(wcr_parsed['floornoise'])

    if wcr_parsed['obss_util'] <= 0:
        conclusion['其它设备占用信道'] = '屏蔽箱:{}'.format(wcr_parsed['obss_util'])
    elif wcr_parsed['obss_util'] <= 10:
        conclusion['其它设备占用信道'] = '无影响:{}'.format(wcr_parsed['obss_util'])
    elif wcr_parsed['obss_util'] <= 15:
        conclusion['其它设备占用信道'] = '低影响:{}'.format(wcr_parsed['obss_util'])
    elif wcr_parsed['obss_util'] <= 20:
        conclusion['其它设备占用信道'] = '受影响:{}'.format(wcr_parsed['obss_util'])
    else:
        conclusion['其它设备占用信道'] = '高影响:{}'.format(wcr_parsed['obss_util'])

    count = 0
    for ap in iwpss_parsed:
        if ap[1] == str(wcr_parsed['channel']):
            count += 1
    conclusion['同信道设备个数（信道号从低到高排序，最多显示前200条，高信道号可能被忽略！）'] = count

    if float(iwps_parsed['Tx fail count PER'].strip('%')) > 10:
        conclusion['TX丢包率'] = '异常:{}'.format(iwps_parsed['Tx fail count PER'])
    else:
        conclusion['TX丢包率'] = '正常:{}'.format(iwps_parsed['Tx fail count PER'])

    if float(iwps_parsed['Rx with CRC PER'].strip('%')) > 10:
        conclusion['RX丢包率'] = '异常:{}'.format(iwps_parsed['Rx with CRC PER'])
    else:
        conclusion['RX丢包率'] = '正常:{}'.format(iwps_parsed['Rx with CRC PER'])

    conclusion['芯片温度'] = iwps_parsed['CurrentTemperature']
    conclusion['温控寄存器状态'] = '寄存器地址:{};寄存器值:{}'.format(
        iwpreg_parsed['mapped_addr'], iwpreg_parsed['value']
    )

    if float(top_cpu['idle'].strip('%')) < 10:
        conclusion['CPU空闲资源'] = '短缺:{}'.format(top_cpu['idle'])
    else:
        conclusion['CPU空闲资源'] = '正常:{}'.format(top_cpu['idle'])

    lines = ['============={}=============\n'.format('结论')]
    for key in conclusion.keys():
        lines.append('{}\t:\t{}\n'.format(key, conclusion[key]))
    lines.append('============={}=============\n'.format('WLANCONFIG RADIO'))
    for key in wcr_parsed.keys():
        lines.append('{}\t:\t{}\n'.format(key, wcr_parsed[key]))
    lines.append('============={}=============\n'.format('IWPRIV SITE-SURVEY'))
    for line in iwpss_parsed:
        lines.append('||'.join(line) + '\n')
    lines.append('============={}=============\n'.format('IWPRIV STAT'))
    for key in iwps_parsed.keys():
        lines.append('{}\t:\t{}\n'.format(key, iwps_parsed[key]))
    lines.append(
        '============={}=============\n'.format('IWPRIV MAC (温控寄存器:{})'.format(params['console']['iwpriv_reg']))
    )
    for key in iwpreg_parsed.keys():
        lines.append('{}\t:\t{}\n'.format(key, iwpreg_parsed[key]))
    lines.append('============={}=============\n'.format('TOP (CPU占用)'))
    lines.append(top)

    with open('reports/check_wireless.txt', 'w') as f:
        f.writelines(lines)

    params['console']['send_string'] = b'\x03'
    params['console']['format'] = 'bytes'
    return params
