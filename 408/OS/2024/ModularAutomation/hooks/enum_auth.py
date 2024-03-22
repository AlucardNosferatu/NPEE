import random
import time


def h0(params):
    logger = params['log']['logger']
    logger.info('使用正确密码【{}】进行登录获取SID'.format(params['eweb']['pass']))
    return params


def h1(params):
    logger = params['log']['logger']
    if params['eweb']['sid'] is None:
        logger.error('警告：正确的密码不能获取SID')
    params['if_switch'] = params['failed_times'] > 0
    time.sleep(1)
    return params


def h2(params):
    logger = params['log']['logger']
    params['eweb']['ip'] = params['设备IP地址']
    params['错误密码_明文'] = list(params['正确密码_明文'])
    # 打乱正确密码作为错误密码
    random.shuffle(params['错误密码_明文'])
    params['错误密码_明文'] = ''.join(params['错误密码_明文'])
    params['eweb']['pass'] = params['错误密码_明文']
    logger.info('使用错误密码【{}】进行登录获取SID'.format(params['eweb']['pass']))
    return params


def h3(params):
    logger = params['log']['logger']
    params['eweb']['ip'] = params['设备IP地址']
    params['eweb']['pass'] = params['正确密码_明文']
    # 伪造超时
    time_struct_now = time.localtime()
    timestamp = int(time.mktime(time_struct_now))
    logger.info('当前实际时间戳【{}】'.format(timestamp))
    timestamp += 666
    logger.info('添加66秒超时的时间戳【{}】'.format(timestamp))
    params['eweb']['timestamp'] = timestamp
    return params


def h4(params):
    logger = params['log']['logger']
    if params['eweb']['sid'] is not None:
        logger.error('警告：错误的密码能够获取SID')
    params['failed_times'] -= 1
    params['if_switch'] = params['failed_times'] > 0
    logger.info('剩余穷举次数【{}】'.format(params['failed_times']))
    time.sleep(1)
    return params


def h5(params):
    logger = params['log']['logger']
    if params['eweb']['sid'] is not None:
        logger.error('警告：超过10次穷举不能锁定正确密码的请求！\n获取到的SID为:{}'.format(params['eweb']['sid']))
    return params
