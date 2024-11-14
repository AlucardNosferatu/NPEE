import json
import time

import paho.mqtt.client as mqtt


def mqtt_init(params):
    def on_con(client, userdata, flags, rc, p=params):
        print("rc:{}".format(rc))
        m_params = p['mqtt']
        if rc == 0:
            print("Connected to MQTT broker")
            # 订阅主题
            if 'topic' in m_params.keys():
                p = mqtt_subscribe(params=p)
            m_params['exception'] = None
        else:
            err_str = "Failed to connect to MQTT broker"
            print(err_str)
            m_params['exception'] = ConnectionError(err_str)

    mqtt_params = params['mqtt']
    client_ = mqtt.Client()
    print('mqtt客户端对象已初始化')
    mqtt_params['client'] = client_
    if 'on_connect' in mqtt_params.keys():
        client_.on_connect = mqtt_params['on_connect']
        print('设置自定义连接后回调')
    else:
        client_.on_connect = on_con
        print('设置默认连接后回调')
    if 'on_message' in mqtt_params.keys():
        client_.on_connect = mqtt_params['on_message']
        print('设置新消息回调')
    port = 1883
    if 'port' in mqtt_params.keys():
        port = mqtt_params['port']
    client_.connect(mqtt_params['host'], port)
    return params


def mqtt_subscribe(params):
    mqtt_params = params['mqtt']
    client_: mqtt.Client = mqtt_params['client']
    client_.subscribe(topic=mqtt_params['topic'])
    return params


def mqtt_publish(params):
    mqtt_params = params['mqtt']
    client_: mqtt.Client = mqtt_params['client']
    print('topic:', mqtt_params['topic'])
    client_.publish(topic=mqtt_params['topic'], payload=mqtt_params['payload'])
    return params


def mqtt_read_start(params):
    def on_msg(client, userdata, msg: mqtt.MQTTMessage, p=params):
        m_params = p['mqtt']
        m_params['msg_queue'].append(msg)
        data = json.loads(s=msg.payload.decode('utf-8'))
        formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
        print(formatted_json)
        if 'queue_length' in m_params.keys() and len(m_params['msg_queue']) > m_params['queue_length']:
            m_params['msg_queue'].pop(0)

    mqtt_params = params['mqtt']
    msg_queue = []
    mqtt_params['msg_queue'] = msg_queue
    client_: mqtt.Client = mqtt_params['client']
    client_.on_message = on_msg
    client_.loop_start()
    return params


def mqtt_read_stop(params):
    mqtt_params = params['mqtt']
    client_: mqtt.Client = mqtt_params['client']
    client_.loop_stop()
    return params


if __name__ == '__main__':
    params_ = {
        'mqtt': {
            'host': '192.168.109.1',
            'topic': 'sys/#'
        }
    }
    params_ = mqtt_init(params=params_)
    params_ = mqtt_read_start(params=params_)
    cd = 10
    while cd > 0:
        time.sleep(1)
        if len(params_['mqtt']['msg_queue']) > 0:
            msg_: mqtt.MQTTMessage = params_['mqtt']['msg_queue'].pop(0)
            msg_ = msg_.payload.decode('utf-8')
            data = json.loads(s=msg_)
            formatted_json_ = json.dumps(data, indent=4, ensure_ascii=False)
            print(formatted_json_)
            cd -= 1
    params_ = mqtt_read_stop(params=params_)
    print('第二轮开始')
    params_ = mqtt_read_start(params=params_)
    while cd < 10:
        time.sleep(1)
        if len(params_['mqtt']['msg_queue']) > 0:
            msg_: mqtt.MQTTMessage = params_['mqtt']['msg_queue'].pop(0)
            msg_ = msg_.payload.decode('utf-8')
            data = json.loads(s=msg_)
            formatted_json_ = json.dumps(data, indent=4, ensure_ascii=False)
            print(formatted_json_)
            cd += 1
    params_ = mqtt_read_stop(params=params_)
