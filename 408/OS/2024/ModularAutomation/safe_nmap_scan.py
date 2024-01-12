import os

from core.flow_chart import FlowChart

if __name__ == '__main__':
    fc = FlowChart()
    fc.load_map(hook_script='nmap_scan.py', map_json='NMAP端口扫描测试.pos')
    end = False
    while not end:
        end = fc.run_step()
    os.abort()
