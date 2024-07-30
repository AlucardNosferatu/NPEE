from core.flow_chart import FlowChart
from modules.watchdog import wake

if __name__ == '__main__':
    params = {
        'watchdog': {
            'port': 20291,
            'ttl': 60,
            'age': 60,
            'watched_params': {}
        }
    }
    fc = FlowChart(prerequisite=params)
    fc.load_map(hook_script='generic_watchdog.py', map_json='看门狗.pos')
    params = {
        'flowchart': {
            'fc_pool': {
                '看门狗': fc
            }
        }
    }
    wake(params=params)
