import os

from core.flow_chart import FlowChart
from modules.webhook_api import webhook_send

if __name__ == '__main__':
    fc = FlowChart(prerequisite={'debug': 'reports/WZRY_C.png'})
    fc.load_map(hook_script='enhance4ocr.py', map_json='图像增强.pos')
    end = False
    while not end:
        end = fc.run_step()
    os.abort()
