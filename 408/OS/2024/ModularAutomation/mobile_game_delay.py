import json
import os

from core.flow_chart import FlowChart
from modules.logger import log_logger_init, log_handler_init
from modules.webhook_api import webhook_send

if __name__ == '__main__':
    params = {}
    params['cv'] = {
        # 'point_ul': {'x': 2289, 'y': 12},
        # 'point_dr': {'x': 2369, 'y': 36},
        'point_ul': {'x': 25, 'y': 25},
        'point_dr': {'x': 125, 'y': 50},
        'delay': 1,
        'filename': 'reports/20240124-103534.mp4'
    }
    fc = FlowChart(prerequisite=params)
    fc.load_map(hook_script='mobile_game_delay.py', map_json='应用延迟测量.pos')
    # todo: makeshift patch
    fc.params_bus['log'] = {'logger_name': 'mobile_game_delay'}
    fc.params_bus = log_logger_init(params=fc.params_bus)
    fc.params_bus = log_handler_init(params=fc.params_bus)
    end = False
    while not end:
        end = fc.run_step()
    os.abort()
