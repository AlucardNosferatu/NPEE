import os

from core.flow_chart import FlowChart

if __name__ == '__main__':
    fc = FlowChart()
    fc.load_map(hook_script='manufacture_throughput.py', map_json='产测吞吐自动化.pos')
    end = False
    while not end:
        end = fc.run_step()
    os.abort()

# postman_body = {
#     "task_params_list": [
#         "manufacture_throughput.py",
#         "产测吞吐自动化.pos",
#         [
#             "MISC",
#             "CONSOLE",
#             "MISC_S",
#             "CHARIOT",
#             "EXCEL"
#         ]
#     ]
# }
