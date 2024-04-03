from modules.http_api import http_post


def webhook_send(params):
    '''
    Webhook机器人通知功能
    params['webhook']['send_string']写入要发的文本
    params['webhook']['webhook_url']写入Webhook URL
    '''
    send_string = params['webhook']['send_string']
    webhook_url = params['webhook']['webhook_url']
    headers = {"Content-Type": "application/json; charset=utf-8"}
    body = {"msg_type": "text", "content": {"text": send_string}}
    # noinspection PyTypeChecker
    params = {'http': {}}
    params['http']['url'] = webhook_url
    params['http']['data'] = body
    params['http']['headers'] = headers
    params = http_post(params=params)
    return params
