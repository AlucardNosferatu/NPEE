from core.flow_chart import FlowChart
from modules.watchdog import fetch, feed

if __name__ == '__main__':
    params = {
        'watchdog': {
            'port': 20291
        }
    }
    params = fetch(params=params)
    if len(list(params.keys())) <= 0:
        params = {
            'todo': 'todo',
            'watchdog': {
                'port': 20291,
                'exe_file': 'example_use_wd.exe'
            }
        }
    fc = FlowChart(prerequisite=params)
    fc.load_map(hook_script='todo.py', map_json='todo.pos')
    end = False
    while not end:
        end = fc.run_step()
        fc.params_bus = feed(params=fc.params_bus)
