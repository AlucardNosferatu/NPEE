import os

from core.flow_chart import FlowChart
from modules.logger import log_logger_init, log_handler_init

if __name__ == '__main__':
    ssh = False
    debug = False
    params = {
        'disable_fm_debug': debug, 'disable_fm_ssh': ssh, 'loop_cd': 4,
        'misc': {
            'sn': None,
            'user': '林昊波',
            'product': 'EW300T',
            'project': 'R302',
            'new_mac_list': []
        }
    }
    if ssh:
        if debug:
            dut_ip = '192.168.110.1'
            ssh_pass = '57e541f69676ce62'
        else:
            dut_ip = '10.44.77.254'
            ssh_pass = 'ruijie@ap#ykhwzx!'
        # noinspection PyTypedDict
        params['console'] = {  # SSH连WAN口模式
            'console_type': 'ssh',
            'dut_ip': dut_ip,
            'ssh_pass': ssh_pass
        }
    else:
        params['console'] = {  # 串口模式
            'console_type': 'serial',
            'port': 'COM5',
            'baud_rate': 57600,
            'serial_pass': 'ruijie@ap#ykhwzx!',
            'serial_type': 'RJ'
        }
    fc = FlowChart(prerequisite=params)
    fc.load_map(hook_script='disable_fm.py', map_json='自动解除产测模式.pos')
    # todo: makeshift patch
    fc.params_bus = log_logger_init(params=fc.params_bus)
    fc.params_bus = log_handler_init(params=fc.params_bus)
    end = False
    while not end:
        end = fc.run_step()
    os.abort()
