import os

from core.flow_chart import FlowChart

if __name__ == '__main__':
    dut_ip = input('输入DUT IP地址，默认192.168.110.1:')
    ssh_pass = input('输入SSH控制台密码，默认2d9e7c0333cd4f5d:')
    if len(dut_ip) <= 0:
        dut_ip = '192.168.110.1'
    if len(ssh_pass) <= 0:
        ssh_pass = '2d9e7c0333cd4f5d'
    params = {
        'console': {  # SSH连WAN口模式
            'console_type': 'ssh',
            'dut_ip': dut_ip,
            'ssh_pass': ssh_pass
        }
    }
    fc = FlowChart(prerequisite=params)
    fc.load_map(hook_script='flash_size.py', map_json='查询Flash容量.pos')
    end = False
    while not end:
        end = fc.run_step()
    os.abort()
