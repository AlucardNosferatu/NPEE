from __future__ import annotations

import time

import paramiko
import serial

from modules.console_parsers.iwconfig import IWConfig
from modules.console_parsers.iwpriv import IWPSiteSurvey, IWPStat, IWPReg
from modules.console_parsers.wlanconfig import WCList, WCRadio


def console_login(params):
    # params = {
    #     'console': {
    #         'console_type': 'ssh',
    #         'dut_ip': '192.168.110.1',
    #         'ssh_pass': '57e541f69676ce62'
    #     }
    # }
    console_login_params = params['console']
    try:
        console_type = console_login_params['console_type']
        if console_type == 'serial':
            console_serial_port = console_login_params['port']
            console_serial_baud_rate = console_login_params['baud_rate']
            ser = serial.Serial(port=console_serial_port,
                                baudrate=console_serial_baud_rate, timeout=0.5)
            if 'serial_type' in console_login_params and console_login_params['serial_type'] == 'RJ':
                console_serial_pass = console_login_params['serial_pass']
                finished = False
                while not finished:
                    echo_string = ser.read_all().decode('utf-8')
                    print(echo_string)
                    if 'root@' in echo_string:
                        finished = True
                    elif 'Ruijie login:' in echo_string or 'Reyee login' in echo_string:
                        ser.write(data='root\r'.encode('utf-8'))
                    elif 'Password:' in echo_string:
                        ser.write(data='{}\r'.format(
                            console_serial_pass).encode('utf-8'))
                    else:
                        ser.write(data='\r'.encode('utf-8'))
                    time.sleep(0.5)
            console_login_params.__setitem__('serial', ser)
        elif console_type == 'ssh':
            console_ssh_ip = console_login_params['dut_ip']
            console_ssh_port = 54133
            console_ssh_user = 'root'
            console_ssh_pass = console_login_params['ssh_pass']
            ssh_ = paramiko.SSHClient()
            ssh_.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_.connect(console_ssh_ip, console_ssh_port,
                         username=console_ssh_user, password=console_ssh_pass)
            ssh_shell = ssh_.invoke_shell()
            console_login_params.__setitem__('ssh', ssh_shell)
        elif console_type == 'telnet':
            raise NotImplementedError(
                'telnet console has not been implemented yet.')
        else:
            raise ValueError(
                'Only telnet, ssh and serial console are supported.')
        console_login_params['exception'] = None
    except Exception as e:
        console_login_params['exception'] = e
    return params


def console_send(params: dict):
    def wait_for_echo(csp):
        if 'wait' in csp.keys():
            wait = csp['wait']
            del csp['wait']
            time.sleep(float(wait))

    console_send_params = params['console']
    try:
        console_type = console_send_params['console_type']
        send_string: str | bytes = console_send_params['send_string']
        del console_send_params['send_string']
        if console_type == 'serial':
            ser: serial.Serial = console_send_params['serial']
            if 'format' not in console_send_params.keys() or console_send_params['format'] == 'str':
                ser.write(data='\r'.encode('utf-8'))
                _ = ser.read_all().decode('utf-8')
                ser.write(data='{}\r'.format(send_string).encode('utf-8'))
                wait_for_echo(csp=console_send_params)
                echo_string = ser.read_all().decode('utf-8')
            elif console_send_params['format'] == 'bytes':
                _ = ser.read_all()
                ser.write(data=send_string)
                wait_for_echo(csp=console_send_params)
                echo_string = ser.read_all()
            else:
                raise ValueError('format should be bytes or str.')
            console_send_params.__setitem__('echo_string', echo_string)
        elif console_type == 'ssh':
            ssh_shell: paramiko.Channel = console_send_params['ssh']
            ssh_shell.send('\r'.encode('utf-8'))
            _ = ssh_shell.recv(65535).decode('utf-8')
            if 'format' not in console_send_params.keys() or console_send_params['format'] == 'str':
                ssh_shell.send('{}\r'.format(send_string).encode('utf-8'))
            elif console_send_params['format'] == 'bytes':
                ssh_shell.send(send_string)
            else:
                raise ValueError('format should be bytes or str.')
            wait_for_echo(csp=console_send_params)
            echo_string = ssh_shell.recv(65535).decode('utf-8')
            console_send_params.__setitem__('echo_string', echo_string)
        elif console_type == 'telnet':
            raise NotImplementedError(
                'telnet console has not been implemented yet.')
        else:
            raise ValueError(
                'Only telnet, ssh and serial console are supported.')
        console_send_params['exception'] = None
    except Exception as e:
        console_send_params['exception'] = e
    return params


def console_get_ap_cli(params):
    params['console']['send_string'] = "iwconfig"
    params['console']['format'] = 'str'
    params['console']['wait'] = 5
    params = console_send(params=params)
    iwconfig_text = params['console']['echo_string']
    del params['console']['echo_string']

    params['console']['send_string'] = "ifconfig"
    params['console']['format'] = 'str'
    params['console']['wait'] = 5
    params = console_send(params=params)
    ifconfig_text = params['console']['echo_string']
    del params['console']['echo_string']

    iwconfig_obj = IWConfig(text=iwconfig_text)
    band_type = params['console']['band_type']
    del params['console']['band_type']
    ei = iwconfig_obj.effective_interface(ifconfig_text, band_type)
    effective_interfaces = []
    for i in ei:
        if not i['ssid'] == '@Ruijie-Repeater':
            effective_interfaces.append(i)
    ap_cli = effective_interfaces[0]["name"]
    params['console']['ap_cli'] = ap_cli
    return params


def console_get_sta_info(params):
    ap_cli = params['console']['ap_cli']
    params['console']['send_string'] = 'wlanconfig {} list'.format(ap_cli)
    params['console']['format'] = 'str'
    params['console']['wait'] = 5
    params = console_send(params=params)
    wlanconfig_text = params['console']['echo_string']
    del params['console']['echo_string']

    sta_mac = params['console']['sta_mac']
    del params['console']['sta_mac']
    wcl_parsed = WCList(text=wlanconfig_text)
    sta_info = wcl_parsed.get_client(mac=sta_mac)
    # sta_info = {
    #     "mac": None, "channel": None, "txrate": None, "rxrate": None, "rssi": None, "maxrate": None,
    #     "accoctime": None, "utilization": None, "floornoise": None, "powersavemode": None, "ifname": None,
    #     "ssid": None, "wifiup": None, "wifidown": None
    # }
    params['console']['sta_info'] = sta_info

    return params


def console_get_radio_info(params):
    ap_cli = params['console']['ap_cli']
    params['console']['send_string'] = 'wlanconfig {} radio'.format(ap_cli)
    params['console']['format'] = 'str'
    params['console']['wait'] = 5
    params = console_send(params=params)
    wlanconfig_text = params['console']['echo_string']
    del params['console']['echo_string']
    wcr_parsed = WCRadio(text=wlanconfig_text).wlanconfig
    params['console']['wcr_parsed'] = wcr_parsed
    return params


def console_iwpriv_site_survey(params):
    ap_cli = params['console']['ap_cli']
    params['console']['send_string'] = 'iwpriv {} set sitesurvey=1'.format(
        ap_cli)
    params['console']['format'] = 'str'
    params['console']['wait'] = 5
    params = console_send(params=params)
    params['console']['send_string'] = 'iwpriv {} get_site_survey'.format(
        ap_cli)
    params['console']['format'] = 'str'
    params['console']['wait'] = 5
    params = console_send(params=params)
    iwpriv_text = params['console']['echo_string']
    del params['console']['echo_string']
    iwpss_parsed = IWPSiteSurvey(text=iwpriv_text).iwp
    params['console']['iwpss_parsed'] = iwpss_parsed
    params['console']['send_string'] = 'iwpriv {} set sitesurvey=0'.format(
        ap_cli)
    params['console']['format'] = 'str'
    params = console_send(params=params)
    return params


def console_iwpriv_stat(params):
    ap_cli = params['console']['ap_cli']
    params['console']['send_string'] = 'iwpriv {} stat'.format(ap_cli)
    params['console']['format'] = 'str'
    params['console']['wait'] = 5
    params = console_send(params=params)
    iwpriv_text = params['console']['echo_string']
    del params['console']['echo_string']
    iwps_parsed = IWPStat(text=iwpriv_text).iwp
    params['console']['iwps_parsed'] = iwps_parsed
    return params


def console_iwpriv_reg(params):
    ap_cli = params['console']['ap_cli']
    iwpriv_mac = params['console']['iwpriv_reg']
    params['console']['send_string'] = 'iwpriv {} mac {}'.format(
        ap_cli, iwpriv_mac)
    params['console']['format'] = 'str'
    params['console']['wait'] = 5
    params = console_send(params=params)
    iwpriv_text = params['console']['echo_string']
    del params['console']['echo_string']
    iwpreg_parsed = IWPReg(text=iwpriv_text).iwp
    params['console']['iwpreg_parsed'] = iwpreg_parsed
    return params


if __name__ == '__main__':
    params_ = {
        'console': {
            'console_type': 'ssh',
            'dut_ip': '192.168.110.1',
            'ssh_pass': '57e541f69676ce62'
        }
    }
    # params_ = {
    #     'console': {
    #         'console_type': 'serial',
    #         'port': 'COM10',
    #         'baud_rate': 115200,
    #         'serial_pass': '1b762f4ae9e6a903',
    #         'serial_type': 'RJ'
    #     }
    # }
    params_ = console_login(params=params_)
    params_['console']['send_string'] = 'top -d1'
    params_['console']['format'] = 'str'
    params_['console']['wait'] = 5
    params_ = console_send(params=params_)
    params_['console']['send_string'] = b'\x03'
    params_['console']['format'] = 'bytes'
    params_ = console_send(params=params_)
    params_['console']['send_string'] = 'uci show sysinfo'
    params_['console']['format'] = 'str'
    params_['console']['wait'] = 5
    params_ = console_send(params=params_)
    # params_['console']['band_type'] = '5G'
    # params_['console']['iwpriv_reg'] = '820d002c'
    # params_ = console_get_ap_cli(params=params_)
    # params_ = console_iwpriv_reg(params=params_)
    print('Done')
