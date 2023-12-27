def h0(params):
    scan_udp, scan_tcp = True, True
    dut_ip = '192.168.110.1'
    params['nmap'] = {}
    params['nmap']['save_txt'] = 'reports/nmap.json'
    params['nmap']['scan_host'] = dut_ip
    params['nmap']['scan_port'] = '1-65535'
    params['nmap']['scan_args'] = '-A -T4 -v -Pn{}{}'.format(
        {True: ' -sU', False: ''}[scan_udp], {True: ' -sT', False: ''}[scan_tcp]
    )

    params['console'] = {
        'console_type': 'ssh',
        'dut_ip': dut_ip,
        'ssh_pass': 'ruijie@ap#ykhwzx!'
    }
    params['console']['send_string'] = 'netstat -au'
    params['console']['format'] = 'str'
    params['console']['wait'] = 2

    params['ns'] = {}
    params['ns']['template_path'] = 'reports/template_ns.xlsx'
    params['ns']['save_path'] = 'reports/nmap.xlsx'
    params = read_template_ns(params=params)
    logger = params['log']['logger']
    logger.info('任务参数已全部装订')
    return params


def h1(params):
    return params


def h2(params):
    echo_string = params['console']['echo_string']
    scan_result = params['nmap']['scan_result']
    tcp = list(scan_result['scan'][params['nmap']['scan_host']]['tcp'].keys())
    udp_scanned = list(scan_result['scan'][params['nmap']['scan_host']]['udp'].keys())
    udp_verified = [udp for udp in udp_scanned if '{}:'.format(udp) in echo_string]
    ports = list(set(tcp + udp_verified))
    type_dict = {True: 'Yes', False: ''}
    is_tcp, is_udp = [type_dict[port in tcp] for port in ports], [type_dict[port in udp_verified] for port in ports]
    data_src_dict = {'ports': ports, 'tcp': is_tcp, 'udp': is_udp}
    params['excel']['data_src_dict'] = data_src_dict
    params['excel']['save_path'] = params['ns']['save_path']
    return params


def read_template_ns(params):
    ns_params = params['ns']
    template_path = ns_params['template_path']
    if 'excel' not in params.keys():
        params['excel'] = {}
    params['excel']['template_path'] = template_path
    return params
