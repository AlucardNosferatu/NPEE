import json
import sqlite3

import pandas as pd
import pymysql
import redis


def db_connect(params):
    db_connect_params = params['database']
    db_type = db_connect_params['db_type']
    if db_type == 'sqlite':
        db_path = db_connect_params['db_path']
        connector = sqlite3.connect(database=db_path)
        db_connect_params['connector'] = connector
    elif db_type == 'mysql':
        db_ip = db_connect_params['db_ip']
        db_port = db_connect_params['db_port']
        db_user = db_connect_params['db_user']
        db_pass = db_connect_params['db_pass']
        db_name = db_connect_params['db_name']
        connector = pymysql.connect(
            host=db_ip, port=db_port, user=db_user, password=db_pass, database=db_name, autocommit=True
        )
        db_connect_params['connector'] = connector
    elif db_type == 'redis':
        db_ip = db_connect_params['db_ip']
        db_port = db_connect_params['db_port']
        db_index = db_connect_params['db_index']
        db_pass = db_connect_params['db_pass']
        connector = redis.Redis(host=db_ip, port=db_port, db=db_index, password=db_pass)
        db_connect_params['connector'] = connector
    else:
        raise ValueError('Only sqlite processor has been implemented for now.')
    return params


def db_disconnect(params):
    db_connect_params = params['database']
    connector = db_connect_params['connector']
    connector.close()
    return params


def db_read_sql(params):
    db_read_sql_params = params['database']
    db_type = db_read_sql_params['db_type']
    if db_type in ['sqlite', 'mysql']:
        connector = db_read_sql_params['connector']
        sql_code = db_read_sql_params['sql_code']
        del db_read_sql_params['sql_code']
        result_df = pd.read_sql(sql=sql_code, con=connector)
        db_read_sql_params['result_df'] = result_df
    else:
        raise ValueError('Only sqlite & mysql processor has been implemented for now.')
    return params


def db_write_sql(params):
    db_params = params['database']
    db_type = db_params['db_type']
    if db_type in ['mysql']:
        connector: pymysql.Connection = db_params['connector']
        sql_code = db_params['sql_code']
        del db_params['sql_code']
        affected_rows = connector.query(sql=sql_code)
        db_params['affected_rows'] = affected_rows
    else:
        raise ValueError('Only mysql processor has been implemented for now.')
    return params


def db_insert_sql(params):
    db_params = params['database']
    db_type = db_params['db_type']
    row_dict = db_params['row_dict']
    if type(row_dict) is dict:
        rd_list = [row_dict]
    else:
        rd_list = row_dict
    for row_dict in rd_list:
        if db_type in ['mysql']:
            db_name = db_params['db_name']
            db_table = db_params['db_table']
            row_key_list = list(row_dict.keys())
            row_val_list = [row_dict[key] for key in row_key_list]
            row_key_str = ', '.join(['`{}`'.format(key) for key in row_key_list])
            row_val_str = ', '.join(["'{}'".format(val) for val in row_val_list])
            sql_code = '''
            INSERT INTO `{}`.`{}` ({}) VALUES ({});
            '''
            sql_code = sql_code.format(db_name, db_table, row_key_str, row_val_str)
            db_params['sql_code'] = sql_code
        else:
            raise ValueError('Only mysql processor has been implemented for now.')
        params = db_write_sql(params=params)
    return params


def db_delete_redis(params):
    db_params = params['database']
    connector: redis.Redis = db_params['connector']
    key = db_params['key']
    if connector.exists(key):
        connector.delete(key)
        db_params['exception'] = None
    else:
        db_params['exception'] = IndexError('Cannot find key:{} in redis.'.format(key))
    return params


def db_write_redis(params):
    db_params = params['database']
    connector: redis.Redis = db_params['connector']
    key = db_params['key']
    value = db_params['value']
    del db_params['value']
    connector.set(name=key, value=json.dumps(value))
    return params


def db_read_redis(params):
    db_params = params['database']
    connector: redis.Redis = db_params['connector']
    key = db_params['key']
    value = connector.get(name=key)
    db_params['value'] = value
    return params


def db_exist_redis(params):
    db_params = params['database']
    connector: redis.Redis = db_params['connector']
    key = db_params['key']
    exists = connector.exists(key)
    db_params['exists'] = {1: True, 0: False}[exists]
    return params


if __name__ == '__main__':
    params_ = {'database': {}}
    params_['database']['db_type'] = 'mysql'
    params_['database']['db_ip'] = '127.0.0.1'
    params_['database']['db_port'] = 3306
    params_['database']['db_user'] = 'root'
    params_['database']['db_pass'] = 'ruijie@mysql#family!'
    params_['database']['db_name'] = 'mac_records'
    params_ = db_connect(params=params_)
    params_['database']['db_table'] = 'mac_records'
    params_['database']['row_dict'] = [
        {
            'mac': '1042D37698ED',
            'sn': 'G1RUBGA002337',
            'user': '林昊波',
            'product': 'H20M',
            'project': 'R226'
        },
        {
            'mac': '2042D37698ED',
            'sn': 'G1RUBGA002337',
            'user': '林昊波',
            'product': 'H20M',
            'project': 'R226'
        },
        {
            'mac': '3042D37698ED',
            'sn': 'G1RUBGA002337',
            'user': '林昊波',
            'product': 'H20M',
            'project': 'R226'
        },
    ]
    params_ = db_insert_sql(params=params_)
    params_['database']['sql_code'] = 'SELECT * FROM mac_records.mac_records;'
    params_ = db_read_sql(params=params_)
    print('Done')
