import cProfile
import os
import pstats

from core.flow_chart import FlowChart
from modules.webhook_api import webhook_send

if __name__ == '__main__':
    profiler = cProfile.Profile()
    profiler.enable()
    params = {
        'wvt': {
            'dut_ip': '192.168.110.1',
            'ssh_pass': '09184c4986463316',
            'save_path': 'reports/EW300T-命令注入.xlsx',
            'eweb_pass': 'LostXmas20291224',
            'tp_size': 4,
            'payload_list': [],
            'slowdown_after': 3480,
            'template_path': 'reports/template_payloads.xlsx',
            'wait_per_injection': 1,
        }
    }
    fc = FlowChart(prerequisite=params)
    fc.load_map(hook_script='cmd_injection.py', map_json='命令注入测试.pos')
    end = False
    while not end:
        end = fc.run_step()
    fc.params_bus['webhook'] = {
        'webhook_url': 'https://open.feishu.cn/open-apis/bot/v2/hook/49487983-e106-49c8-a527-4b8a4dfeddf5',
        'send_string': '命令注入已完成'
    }
    fc.params_bus = webhook_send(params=fc.params_bus)
    profiler.disable()
    pstats.Stats(
        profiler, stream=open('reports/性能分析-命令注入.txt', 'w')
    ).sort_stats(pstats.SortKey.CUMULATIVE).print_stats(.3)
    os.abort()
