import random
import string

debug = True
ssh = True
ab_addr = '127.0.0.1'


def h1(params):
    logger = params['log']['logger']
    params['misc'] = {
        'sn': 'G1RUBGA002337',
        'user': '林昊波',
        'product': 'H20M',
        'project': 'R226'
    }
    params['misc']['new_mac_list'] = []
    params['loop_cd'] = 4
    logger.info({True: '使用SSH连接设备', False: '使用串口连接设备'}[ssh])
    logger.info({True: '当前运行模式为DEBUG模式', False: '当前运行模式为RUN模式'}[debug])
    if ssh:
        if debug:
            dut_ip = '192.168.110.1'
            ssh_pass = '57e541f69676ce62'
        else:
            dut_ip = '10.44.77.254'
            ssh_pass = 'ruijie@ap#ykhwzx!'
        params['console'] = {  # SSH连WAN口模式
            'console_type': 'ssh',
            'dut_ip': dut_ip,
            'ssh_pass': ssh_pass
        }
    else:
        params['console'] = {  # 串口模式
            'console_type': 'serial',
            'port': 'COM4',
            'baud_rate': 115200,
            'serial_pass': 'ruijie@ap#ykhwzx!',
            'serial_type': 'RJ'
        }
    # 指定SN
    serial_number = 'MACC4607H30M3'
    # # 不指定SN（生成新的随机SN）
    # serial_number = None
    logger.info({True: '使用随机生成的序列号', False: '使用人工指定的序列号'}[serial_number is None])
    if serial_number is None:
        serial_number = 'MACC' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))
    logger.info('##########注意！##########')
    logger.info('##########注意！##########')
    logger.info('##########注意！##########')
    logger.info('设备新SN号为:{}'.format(serial_number))
    with open(file='reports/SN.txt', mode='a') as f:
        f.write(serial_number + '\n')
    batch_cmd = [
        'setmac {}', 'setsn {}'.format(serial_number), 'fw_setmac factory-mode 0', 'firstboot', 'sync', 'reboot'
    ]
    if debug:
        params['console']['send_string'] = 'uci show sysinfo'
    else:
        params['console']['send_string'] = '\n'.join(batch_cmd)
    params['console']['format'] = 'str'
    params['console']['wait'] = 5
    return params


def h2(params):
    return params


def h3(params):
    params['database']['sql_code'] = 'SELECT * FROM mac_records.mac_records;'
    return params


def h4(params):
    params['misc']['base_mac'] = params['misc']['new_mac']
    params['misc']['new_mac_list'].append(params['misc']['new_mac'])
    params['loop_cd'] -= 1
    if params['loop_cd'] <= 0:
        params['if_switch'] = True
    else:
        params['if_switch'] = False
    return params


def h5(params):
    logger = params['log']['logger']
    logger.info({True: '使用远程数据库比对MAC', False: '使用本地记事本比对MAC'}['database' in params.keys()])
    if 'database' in params.keys():
        result_df = params['database']['result_df']
        mac_record = dict(result_df)['mac'].tolist()
    else:
        mac_record = params['misc']['mac_record']
    mac_record = [record.lower().replace(':', '') for record in mac_record]
    found = False
    for mac in params['misc']['new_mac_list']:
        mac = mac.lower().replace(':', '')
        if mac in mac_record:
            logger.info('记录中已存在该地址:{}'.format(mac))
            found = True
            break
    params['if_switch'] = found
    return params


def h6(params):
    base_mac = params['misc']['new_mac_list'][0]
    params['console']['send_string'] = params['console']['send_string'].format(base_mac.replace(':', ''))
    logger = params['log']['logger']
    logger.info({True: '使用远程数据库记录MAC', False: '使用本地记事本记录MAC'}['database' in params.keys()])
    if 'database' in params.keys():
        params['database']['row_dict'] = []
        for mac in params['misc']['new_mac_list']:
            row_dict = {
                'mac': mac.upper().replace(':', ''),
                'sn': params['misc']['sn'],
                'user': params['misc']['user'],
                'product': params['misc']['product'],
                'project': params['misc']['project']
            }
            params['database']['row_dict'].append(row_dict)
    else:
        for mac in params['misc']['new_mac_list']:
            assert mac not in params['misc']['mac_record']
            params['misc']['mac_record'].append(mac)
    return params


def h7(params):
    params['database'] = {}
    params['database']['db_type'] = 'mysql'
    params['database']['db_ip'] = db_addr
    params['database']['db_port'] = 3306
    params['database']['db_user'] = 'root'
    params['database']['db_pass'] = 'ruijie@mysql#family!'
    params['database']['db_name'] = 'mac_records'
    params['database']['db_table'] = 'mac_records'
    return params
