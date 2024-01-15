import datetime
import time

from modules.console import console_login, console_send
from modules.http_api import http_post


def rs_init(params):
    rs_init_params = params['rotate_shelf']
    rs_port = rs_init_params['port']
    rs_baud = rs_init_params['baud_rate']
    params['console'] = {
        'console_type': 'serial',
        'port': rs_port,
        'baud_rate': rs_baud,
        'serial_type': 'rs'
    }
    params = console_login(params=params)
    rs_init_params['current_angle'] = 0
    rs_init_params['full_loop_time'] = None
    return params


def rs_set_flt(params):
    rs_set_flt_params = params['rotate_shelf']
    flt_seconds_float = rs_set_flt_params['new_flt']
    del rs_set_flt_params['new_flt']
    seconds = int(flt_seconds_float)
    microseconds = int((flt_seconds_float - seconds) * 1000000)
    rs_set_flt_params['full_loop_time'] = datetime.timedelta(seconds=seconds, microseconds=microseconds)
    print('A new FLT is set!')
    print('Time for a full loop:{}'.format(rs_set_flt_params['full_loop_time']))
    return params


def rs_raw_forward(params):
    params['console']['send_string'] = 'forward#'
    params['console']['format'] = 'str'
    params = console_send(params=params)
    return params


def rs_raw_backward(params):
    params['console']['send_string'] = 'backward#'
    params['console']['format'] = 'str'
    params = console_send(params=params)
    return params


def rs_raw_stop(params):
    params['console']['send_string'] = 'stop#'
    params['console']['format'] = 'str'
    params = console_send(params=params)
    return params


def rs_calibrate_start(params):
    params = rs_raw_forward(params=params)
    calibrate_start = datetime.datetime.now()
    params['rotate_shelf']['calibrate_start'] = calibrate_start
    return params


def rs_calibrate_end(params):
    params = rs_raw_stop(params=params)
    calibrate_end = datetime.datetime.now()
    calibrate_start = params['rotate_shelf']['calibrate_start']
    del params['rotate_shelf']['calibrate_start']
    new_flt = calibrate_end - calibrate_start
    print('Full Loop Duration was calibrated:{}'.format(new_flt))
    new_flt = new_flt.seconds + new_flt.microseconds / 1000000
    params['rotate_shelf']['new_flt'] = new_flt
    return params


def rs_calibrate_cmd(params):
    _ = input('Press any key to rotate the shelf to the start position.(forward)')
    params = rs_raw_forward(params=params)
    _ = input('Press any key to stop the shelf at the start position.')
    params = rs_raw_stop(params=params)
    _ = input('Press any key to rotate the shelf to the start position.(backward)')
    params = rs_raw_backward(params=params)
    _ = input('Press any key to stop the shelf at the start position.')
    params = rs_raw_stop(params=params)
    _ = input('Press any key to start rotating and recording time for a full loop.(forward)')
    params = rs_calibrate_start(params=params)
    _ = input('Press any key when the shelf rotate a full loop.')
    params = rs_calibrate_end(params=params)
    return params


def rs_send_calib(params):
    new_flt = params['rotate_shelf']['new_flt']
    del params['rotate_shelf']['new_flt']
    # url = 'http://10.52.0.148:8000/api/ui/ctrlMotor'
    send_calib_url = params['rotate_shelf']['send_calib_url']
    del params['rotate_shelf']['send_calib_url']
    params['http'] = {}
    params['http']['url'] = send_calib_url
    params['http']['data'] = {'new_flt': new_flt}
    params = http_post(params=params)
    return params


def rs_rotate(params):
    direction = params['rotate_shelf']['direction']
    del params['rotate_shelf']['direction']
    angle = params['rotate_shelf']['angle']
    del params['rotate_shelf']['angle']
    if direction in ['forward', 'backward']:
        full_loop_time = params['rotate_shelf']['full_loop_time']
        time_rotate = full_loop_time * angle / 360
        sec_in_float = time_rotate.seconds + time_rotate.microseconds / 1000000
        print('Rotation started, time:{}, direction:{}'.format(sec_in_float, direction))
        params = {'forward': rs_raw_forward, 'backward': rs_raw_backward}[direction](params=params)
        time.sleep(sec_in_float)
        params = rs_raw_stop(params=params)
        print('Rotation stopped, time:{}, direction:{}'.format(sec_in_float, direction))
    else:
        raise ValueError('direction should be "forward" or "backward".')
    return params
