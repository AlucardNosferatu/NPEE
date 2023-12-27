import os

from core.flow_chart import FlowChart

if __name__ == '__main__':
    fc = FlowChart()
    fc.load_map(hook_script='check_wireless.py', map_json='吞吐过低排查工具.pos')
    end = False
    while not end:
        end = fc.run_step()
    os.abort()
