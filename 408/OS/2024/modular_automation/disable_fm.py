import os

from core.flow_chart import FlowChart
from modules.logger import log_logger_init, log_handler_init

if __name__ == '__main__':
    fc = FlowChart()
    fc.load_map(hook_script='disable_fm.py', map_json='自动解除产测模式.pos')
    # todo: makeshift patch
    fc.params_bus = log_logger_init(params=fc.params_bus)
    fc.params_bus = log_handler_init(params=fc.params_bus)
    end = False
    while not end:
        end = fc.run_step()
    os.abort()
