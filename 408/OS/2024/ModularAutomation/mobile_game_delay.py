import json
import os

from core.flow_chart import FlowChart
from modules.logger import log_logger_init, log_handler_init
from modules.webhook_api import webhook_send

if __name__ == '__main__':
    params = {
        'cv': {
            'ocr_extra_config': '-c tessedit_char_whitelist=0123456789ms --psm 6'
        }
    }
    print('OCR精度有限，持续改进中！')

    enhance = input('输入图像强化处理流程参数的JSON文件路径\n默认为"reports/enhance4ocr.json"\n输入"NO_ENHANCE"则不进行图像强化:')
    if enhance != 'NO_ENHANCE':
        if enhance == '':
            enhance = 'reports/enhance4ocr.json'
        params_from_json = json.loads(
            s='\n'.join(
                open(
                    file=enhance,
                    mode='r', encoding='utf-8'
                ).readlines()
            )
        )
        params['flowchart'] = params_from_json
    filename = input('输入本地视频文件路径，例："reports/20240125-155202.mp4"\n不输入则采用在线监测识别（最短采样周期约等于6s）：')
    if filename != '':
        params['cv']['filename'] = filename
        skip = input('输入跳帧个数，不输入默认12帧，输入0为取消跳帧（逐帧处理，贼慢）')
        if skip == '':
            skip = '12'
        params['skip'] = int(skip)
        webhook_url = input('输入飞书机器人Webhook地址，处理完会通知你，如果不填默认通知给林昊波，不需要通知填写DISABLE_NOTIFICATION')
        if webhook_url == '':
            webhook_url = 'https://open.feishu.cn/open-apis/bot/v2/hook/49487983-e106-49c8-a527-4b8a4dfeddf5'
    else:
        webhook_url = 'DISABLE_NOTIFICATION'
    fc = FlowChart(prerequisite=params)
    fc.load_map(hook_script='mobile_game_delay.py', map_json='应用延迟测量.pos')
    # todo: makeshift patch
    fc.params_bus['log'] = {'logger_name': 'mobile_game_delay'}
    fc.params_bus = log_logger_init(params=fc.params_bus)
    fc.params_bus = log_handler_init(params=fc.params_bus)
    end = False
    while not end:
        end = fc.run_step()
    if webhook_url != 'DISABLE_NOTIFICATION':
        fc.params_bus['webhook'] = {
            'webhook_url': webhook_url,
            'send_string': '视频解析已完成'
        }
        fc.params_bus = webhook_send(params=fc.params_bus)
    os.abort()
