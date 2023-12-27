import json
import logging
import os
import sys

from core.flow_chart import FlowChart
from modules.logger import log_logger_init, log_handler_init

if __name__ == '__main__':
    try:
        assert len(sys.argv) == 4
        _, prerequisite, hook_script, map_json = tuple(sys.argv)
        prerequisite = json.loads(s=prerequisite)
        fc = FlowChart(prerequisite=prerequisite)
        fc.load_map(hook_script=hook_script, map_json=map_json)
        # todo: makeshift patch
        fc.params_bus = log_logger_init(params=fc.params_bus)
        fc.params_bus = log_handler_init(params=fc.params_bus)
        fc.params_bus['log']['logger']: logging.Logger
        fc.params_bus['log']['logger'].debug('\n'.join([map_json, hook_script, json.dumps(obj=prerequisite, indent=4)]))
        end = False
        while not end:
            end = fc.run_step()
        os.abort()
    except Exception as e:
        with open('error.txt', 'w') as f:
            f.write(repr(e))
