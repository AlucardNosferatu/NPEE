import datetime
import locale
import logging
import os
from logging.handlers import RotatingFileHandler

from modules.misc import time_format

locale.setlocale(locale.LC_CTYPE, 'Chinese')


def log_logger_init(params):
    if 'log' not in params.keys():
        params['log'] = {}
    log_params = params['log']
    if 'logger_name' in log_params.keys():
        logger_name = log_params['logger_name']
    else:
        logger_name = None
    logger = logging.getLogger(name=logger_name)
    log_level = logging.DEBUG
    if 'log_level' in log_params.keys():
        if log_params['log_level'] in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            log_level = eval('logging.{}'.format(log_params['log_level']))
    logger.setLevel(log_level)
    log_params['logger'] = logger
    return params


def log_handler_init(params):
    log_params = params['log']
    log_max_bytes = 1024 * 1024
    if 'log_max_bytes' in log_params.keys():
        log_max_bytes = log_params['log_max_bytes']
    log_backup_count = 1000
    if 'log_backup_count' in log_params.keys():
        log_backup_count = log_params['log_backup_count']
    sub_folder = ''
    if 'logger_name' in log_params.keys():
        sub_folder = '/{}'.format(log_params['logger_name'])
    log_folder = 'logs{}'.format(sub_folder)
    if not os.path.exists(log_folder):
        os.makedirs(name=log_folder)
    handler = RotatingFileHandler(
        os.path.join(log_folder, '{}.log'.format(datetime.datetime.now().strftime(time_format))),
        maxBytes=log_max_bytes,
        backupCount=log_backup_count
    )
    log_level = logging.DEBUG
    if 'log_level' in log_params.keys():
        if log_params['log_level'] in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            log_level = eval('logging.{}'.format(log_params['log_level']))
    handler.setLevel(log_level)
    # 创建日志格式器
    formatter = logging.Formatter("%(thread)d - %(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # 设置日志格式器
    handler.setFormatter(formatter)
    log_params['handler'] = handler
    if 'logger' in log_params.keys():
        log_params['logger'].addHandler(handler)
    return params
