import datetime
import os

from scapy.volatile import RandMAC

from modules.encryption.eweb_password import encrypt_pass

time_format = "%Y年%m月%d日-%H时%M分%S秒"


def nop(params):
    return params


def eweb_pass_enc(params):
    misc_params = params['misc']
    ep_dec = misc_params['ep_dec']
    ep_enc = encrypt_pass(message=ep_dec)
    misc_params['ep_enc'] = ep_enc
    return params


def timer(params):
    misc_params = params['misc']
    timer_params = misc_params['timer']
    while not timer_params['start']:
        pass
    timer_params['time_start'] = datetime.datetime.now()
    while not timer_params['stop']:
        timer_params['time_end'] = datetime.datetime.now()
        timer_params['time_delta'] = timer_params['time_end'] - \
            timer_params['time_start']
    return params


def process_kill(params):
    misc_params = params['misc']
    kill_processes = misc_params['kill_processes']
    for i in range(len(kill_processes)):
        pid = kill_processes[i]
        try:
            os.system('taskkill /f /pid {}'.format(pid))
            print('结束pids   {}'.format(str(pid)))
            kill_processes[i] = [pid, True, None]
        except Exception as e:
            print('异常:{}'.format(repr(e)))
            kill_processes[i] = [pid, False, e]
    return params


def mac_generate(params):
    misc_params = params['misc']
    finished = False
    new_mac = None
    while not finished:
        new_mac = str(RandMAC())
        if new_mac[1].lower() in ['1', '3', '5', '7', '9', 'b', 'd', 'f']:
            continue
        finished = True
    assert new_mac is not None
    misc_params['new_mac'] = new_mac
    return params


def mac_increase(params):
    misc_params = params['misc']
    base_mac = misc_params['base_mac']
    # base_mac = '00:d0:f8:22:31:29'
    mac_str_hex = base_mac.replace(':', '')
    mac_dec = int(mac_str_hex, 16)
    mac_dec_new = mac_dec + 1
    new_mac = str(hex(mac_dec_new)).split('x')[1]
    while len(new_mac) < 12:
        new_mac = '0' + new_mac
    new_mac = list(new_mac)
    new_mac.insert(2, ':')
    new_mac.insert(4 + 1, ':')
    new_mac.insert(6 + 2, ':')
    new_mac.insert(8 + 3, ':')
    new_mac.insert(10 + 4, ':')
    new_mac = ''.join(new_mac)
    misc_params['new_mac'] = new_mac
    return params


def mac_read_record(params):
    misc_params = params['misc']
    if 'mac_record_file' not in misc_params.keys():
        mac_record_file = 'reports/mac_record.txt'
    else:
        mac_record_file = misc_params['mac_record_file']
    if not os.path.exists(mac_record_file):
        with open(file=mac_record_file, mode='w') as f:
            f.writelines([])
    with open(file=mac_record_file, mode='r') as f:
        mac_record = f.readlines()
        mac_record = [mac.strip() for mac in mac_record]
    misc_params['mac_record'] = mac_record
    return params


def mac_write_record(params):
    misc_params = params['misc']
    if 'mac_record_file' not in misc_params.keys():
        mac_record_file = 'reports/mac_record.txt'
    else:
        mac_record_file = misc_params['mac_record_file']
    if not os.path.exists(mac_record_file):
        with open(file=mac_record_file, mode='w') as f:
            f.writelines([])
    if 'mac_record' not in misc_params.keys():
        mac_record = []
    else:
        mac_record = misc_params['mac_record']
    with open(file=mac_record_file, mode='w') as f:
        f.writelines('\n'.join(mac_record))
    return params


def mac_input_record(params):
    params['misc'] = {}
    params['misc']['new_mac_list'] = []
    for i in range(4):
        if i == 0:
            params['misc']['new_mac'] = input(
                '输入已知MAC的起始地址（例:38:db:35:46:82:a3）').lower()
        else:
            params = mac_increase(params=params)
        params['misc']['base_mac'] = params['misc']['new_mac']
        params['misc']['new_mac_list'].append(params['misc']['new_mac'])
    params = mac_read_record(params=params)
    for mac in params['misc']['new_mac_list']:
        if mac not in params['misc']['mac_record']:
            params['misc']['mac_record'].append(mac)
    params = mac_write_record(params=params)
    [print(mac) for mac in params['misc']['new_mac_list']]
    return params


def mac_input_record_loop(params):
    while True:
        params = mac_input_record(params=params)
        cmd = input('按任意键输入下一个MAC，输入exit退出')
        if cmd == 'exit':
            break


def iface_ip(params):
    misc_params = params['misc']
    iface_name = misc_params['iface_name']
    with os.popen('ipconfig') as fp:
        bf = fp.buffer.read()
        try:
            lines = bf.decode().strip()
        except UnicodeDecodeError:
            lines = bf.decode('gbk').strip()
    lines = lines.replace('\r', '\n')
    while '\n\n' in lines:
        lines = lines.replace('\n\n', '\n')
    lines = lines.split('\n')
    lines.pop(0)
    all_iface_dict = {}
    current_iface = ''
    for line in lines:
        if not line.startswith('   '):
            current_iface = line.strip()
            all_iface_dict[current_iface] = {}
        else:
            line_pair = line.split('. . . . . . . :')
            key1, val = line_pair[0].strip(), line_pair[1].strip()
            all_iface_dict[current_iface][key1] = val
    misc_params['iface_ip'] = None
    for key1 in all_iface_dict.keys():
        if iface_name in key1:
            for key2 in all_iface_dict[key1].keys():
                if 'IPv4 地址' in key2:
                    misc_params['iface_ip'] = all_iface_dict[key1][key2]
    return params


def ip_ping(params):
    misc_params = params['misc']
    ping_host = misc_params['ping_host']
    ping_times = misc_params['ping_times']
    # 在Linux/Mac上使用-c参数，在Windows上使用-n参数
    response = os.system(f"ping -n {ping_times} {ping_host}")
    if response == 0:
        misc_params['ping_result'] = [True, f"{ping_host}可达"]
    else:
        misc_params['ping_result'] = [False, f"{ping_host}不可达"]
    return params


if __name__ == '__main__':
    params_ = {'misc': {'iface_name': '上网用'}}
    iface_ip(params=params_)
    print('Done')
