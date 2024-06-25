import json
import os

import requests

from core.flow_chart import FlowChart
from modules.logger import log_logger_init, log_handler_init
from modules.webhook_api import webhook_send
from power_cycle_daemon import custom_serializer

ip = 'localhost'
port = 20291
base_url = 'http://{}:{}'.format(ip, port)
params = {}
print('服务端端口:{}'.format(port))


def get_params_from_server():
    global params
    server_url = '{}/assign_worker'.format(base_url)  # 服务端接口地址
    finished = False
    while not finished:
        try:
            response = requests.get(server_url)  # 发起 GET 请求
            if response.status_code == 200:
                data = response.json()  # 解析 JSON 格式的响应数据
                # print('服务器返回data:{}'.format(data))
                params = data['data']['params']  # 获取服务端返回的 params 变量
                finished = True
                print('最新数据已从服务端获取')
            else:
                print(f"请求失败: {response.status_code} - {response.reason}")
        except requests.RequestException as e:
            print(f"请求发生异常: {e}")


def send_params_to_server():
    global params
    server_url = '{}/report_result'.format(base_url)  # 服务端接口地址
    data = {'params': params, 'pid': str(os.getpid())}
    data = json.dumps(obj=data, default=custom_serializer)
    # print('序列化params:{}'.format(data))
    finished = False
    while not finished:
        try:
            response = requests.post(server_url, data=data)  # 发起 GET 请求
            if response.status_code == 200:
                # data = response.json()  # 解析 JSON 格式的响应数据
                # params = data['data']['params']  # 获取服务端返回的 params 变量
                finished = True
                print('最新数据已提交至服务端')
            else:
                print(f"请求失败: {response.status_code} - {response.reason}")
        except requests.RequestException as e:
            print(f"请求发生异常: {e}")


if __name__ == '__main__':
    get_params_from_server()
    fc = FlowChart(prerequisite=params)
    fc.load_map(hook_script='power_cycle.py', map_json='电源切变循环测试.pos')
    # todo: makeshift patch
    fc.params_bus['log'] = {'logger_name': 'power_cycle', 'log_backup_count': 8192}
    fc.params_bus = log_logger_init(params=fc.params_bus)
    fc.params_bus = log_handler_init(params=fc.params_bus)
    end = False
    while not end:
        end = fc.run_step()
        params = fc.params_bus
        send_params_to_server()
    fc.params_bus = webhook_send(params=fc.params_bus)
