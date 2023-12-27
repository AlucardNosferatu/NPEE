import copy
import time

import numpy as np
import serial

from modules.console import console_login, console_send


def write_d10_list(angle):
    def d2h(ang):
        tmp = np.frombuffer(buffer=hex(ang & 0xFFFFFFFF).replace('0x', '').zfill(8).upper().encode(), dtype=np.uint8)
        hex_ = ' '.join([hex(t).replace('0x', '') for t in tmp])
        return hex_

    # angle = angle%360  #角度化为360范围
    # 转成8个十六进制数据位
    angle = d2h(angle)

    angel_hex_ori = angle
    end_flag = ['03']
    # 换成列表进行处理,构建符合指令的数据位
    angel_hex_ori = angel_hex_ori.split(' ')

    angel_code_list1 = angel_hex_ori[0:2]
    angel_code_list2 = angel_hex_ori[2:4]
    angel_code_list3 = angel_hex_ori[4:6]
    angel_code_list4 = angel_hex_ori[6:8]
    # 深拷贝
    angel_code_swap = copy.deepcopy(angel_code_list4)
    angel_code_swap.extend(angel_code_list3)
    angel_code_swap.extend(angel_code_list2)
    angel_code_swap.extend(angel_code_list1)
    # 添加头部
    d10_list_head = [b'02', b'31', b'31', b'30', b'31', b'34', b'30', b'34']
    # 去掉不用加和的 02 起始位
    d10_list_head = [i.decode(encoding="utf-8") for i in d10_list_head[1:]]
    # 求和 头部和数据位
    d10_list_head.extend(angel_code_swap)
    # 字符型换成整型才能实现加法
    d10_list_head.extend(end_flag)
    d10_list_chr_ten = [int(v, 16) for v in d10_list_head]
    d10_sum_list = hex(sum(d10_list_chr_ten)).upper()
    # 取求和后的后两位转成十六进制ASCII
    d10_sum_list_check_code = [hex(ord(v.upper()))[2:] for v in d10_sum_list[-2:]]
    # 添加起始符，终止符，和校验位
    d10_sum_list = ['02']
    d10_sum_list.extend(d10_list_head)
    # end_flag = ['03']
    # d10_sum_list.extend(end_flag)
    d10_sum_list.extend(d10_sum_list_check_code)
    # 转换为字节型发送
    d10_sum_list = [i.encode(encoding="utf-8") for i in d10_sum_list]
    return d10_sum_list


def rp_summary_action(params, status, msg, current_angle=None):
    params['rotate_platform']['status'] = status
    params['rotate_platform']['msg'] = msg
    if current_angle is not None:
        params['rotate_platform']['current_angle'] = current_angle
    return params


def rp_init(params):
    rp_init_params = params['rotate_platform']
    rp_port = rp_init_params['port']
    rp_baud = rp_init_params['baud_rate']
    params['console'] = {
        'console_type': 'serial',
        'port': rp_port,
        'baud_rate': rp_baud,
        'serial_type': 'RP'
    }
    params = console_login(params=params)
    ser: serial.Serial = params['console']['serial']
    ser.bytesize = 7
    ser.stopbits = 1
    ser.parity = 'E'
    rp_init_params['current_angle'] = 0
    return params


def rp_set_angle(params):
    rp_sa_params = params['rotate_platform']
    target_angle = rp_sa_params['target_angle']
    del rp_sa_params['target_angle']
    if target_angle < 0 or target_angle > 360:
        params = rp_summary_action(params=params, status=False, msg='角度设置区间0~360')
    else:
        bytes_list = write_d10_list(0)
        for b in bytes_list:
            params['console']['send_string'] = b
            params['console']['format'] = 'bytes'
            params = console_send(params=params)

        delta_angle = target_angle - rp_sa_params['current_angle']
        bytes_list = write_d10_list(delta_angle)
        for b in bytes_list:
            params['console']['send_string'] = b
            params['console']['format'] = 'bytes'
            params = console_send(params=params)

        if params['console']['echo_string'] == b'\x06':
            params = rp_summary_action(
                params=params, status=True, msg=params['console']['echo_string'], current_angle=target_angle
            )
            time.sleep(abs(delta_angle) * 0.2)
        else:
            params = rp_summary_action(
                params=params, status=False, msg=params['console']['echo_string']
            )
    return params


def rp_reset_angle(params):
    params['rotate_platform']['target_angle'] = -1 * params['rotate_platform']['current_angle']
    params = rp_set_angle(params=params)
    return params


if __name__ == '__main__':
    params_ = rp_init(
        params={
            'rotate_platform': {
                'port': 'COM3',
                'baud_rate': 115200,
            }
        }
    )
    params_['rotate_platform']['target_angle'] = 45
    params_ = rp_set_angle(params=params_)
    print('Done')
