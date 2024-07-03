import copy
import datetime
import json
import random
import string
import threading
import time

from kill_thread import kill_thread

from core.flow_chart import FlowChart


def h0(params):
    params = read_template_ci(params=params)
    return params


def h1(params):
    if 'console' not in params.keys():
        params['console'] = {}
    params['console'] = {
        'console_type': 'ssh',
        'dut_ip': params['wvt']['dut_ip'],
        'ssh_pass': params['wvt']['ssh_pass']
    }
    worker_fc: FlowChart = params['flowchart']['fc_pools'][params['flowchart']['old_fc_name']]
    worker_fc.params_bus['console'] = params['console']
    worker_fc.params_bus['wvt'] = params['wvt']
    worker_fc.params_bus['flowchart'] = {
        'given_fc': worker_fc
    }
    return params


def h2(params):
    logger = params['log']['logger']
    all_cases = []
    # 这逼玩意就是等待执行的用例队列
    case_params = params['excel']['case_params']
    api = case_params['api']
    cmd_str = case_params['cmd']
    # logger.info('注入的cmd:\n{}'.format(cmd_str))
    method_ = case_params['method']
    payloads = case_params['payloads']
    for i in range(len(api)):
        cmd_dict = json.loads(cmd_str[i])
        i_list = walk_cmd_dict(cmd_dict=cmd_dict, dont_swap=[['module']])
        for k in range(len(i_list)):
            cmd_dict_copy = copy.deepcopy(cmd_dict)
            set_cmd_dict(cmd_dict=cmd_dict_copy, index_list=i_list[k], value='flagthn')
            cmd_str_ = json.dumps(cmd_dict_copy)
            for j in range(len(payloads)):
                case = {'api': api[i], 'cmd': cmd_str_, 'method': method_[i], 'payload': payloads[j]}
                if 'slowdown_after' in params['wvt'].keys() and i >= params['wvt']['slowdown_after']:
                    case['slow_inject'] = True
                all_cases.append(case)
        logger.info('请求载荷预处理进度:{:.2%}'.format(i / len(api)))
    params['wvt']['testcases'] = all_cases
    params['wvt']['queue'] = all_cases.copy()
    params['flowchart'] = {
        "old_fc_name": "命令注入执行",
        "new_fc_name": "命令注入执行",
        "new_fc_pre": {},
        "new_fc_hook": "cmd_injection_worker.py",
        "new_fc_map": "命令注入执行.pos",
        "locks": {
            "命令注入执行": threading.Lock()
        }
    }
    return params


def h3(params):
    queue = params['wvt']['queue']
    if len(queue) > 0:
        params['if_switch'] = True
    else:
        params['if_switch'] = False
    return params


def h4(params):
    logger = params['log']['logger']
    tp_size = params['wvt']['tp_size']
    if 'slow_inject' in params['wvt']['queue'][0].keys() and params['wvt']['queue'][0]['slow_inject']:
        tp_size = 1
        logger.info('特殊用例，取消并发请求')
    thread_pool = params['thread_pool']
    logger.info('当前线程池大小:{}'.format(len(thread_pool)))
    if len(thread_pool) < tp_size:
        params['if_switch'] = True
    else:
        params['if_switch'] = False
    return params


def h5(params):
    thread_pool = params['thread_pool']
    if len(thread_pool) > 0:
        params['if_switch'] = True
    else:
        params['if_switch'] = False
    return params


def h6(params):
    params = pop_old_thread(params)
    params = h4(params=params)
    return params


def h7(params):
    logger = params['log']['logger']
    if 'injected_cmd' not in params['wvt'].keys():
        params['wvt']['injected_cmd'] = []
        params['wvt']['injected_api'] = []
        params['wvt']['inject_method'] = []
    if len(params['wvt']['injected_cmd']) >= params['wvt']['tp_size']:
        logger.info('发送缓冲区（最多{}个请求）已满，不添加新请求，直接开始执行'.format(params['wvt']['tp_size']))
    else:
        queue = params['wvt']['queue']
        next_case = queue.pop(0)
        cmd_str = next_case['cmd']
        payload = next_case['payload']
        if 'payload_list' not in params['wvt'].keys():
            params['wvt']['payload_list'] = []
        injected_filename = "_".join(
            [
                "injected",
                datetime.datetime.now().strftime("%H%M%S"),
                ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
            ]
        )
        params['wvt']['payload_list'].append(injected_filename)
        payload = payload.replace('占位符', injected_filename)
        cmd_str = cmd_str.replace('flagthn', payload)
        try:
            cmd_dict = json.loads(cmd_str)
        except Exception as e:
            _ = e
            cmd_dict = eval(cmd_str)
        params['wvt']['injected_cmd'].append(cmd_dict)
        params['wvt']['injected_api'].append(next_case['api'])
        params['wvt']['inject_method'].append(next_case['method'])
        if 'module' in cmd_dict.keys():
            injected_module = cmd_dict['module']
        else:
            injected_module = None
        progress = 1 - (len(params['wvt']['queue']) / len(params['wvt']['testcases']))
        logger.info(
            '注入API:{} 注入方法:{} 注入模块:{} 进度:{:.2%}={}/{}'.format(
                next_case['api'], next_case['method'], injected_module, progress,
                len(params['wvt']['testcases']) - len(params['wvt']['queue']),
                len(params['wvt']['testcases'])
            )
        )
    if 'wait_per_injection' in params['wvt'].keys():
        time.sleep(params['wvt']['wait_per_injection'])
    # 手动重置子图运行状态
    fc_params = params['flowchart']
    old_fc_name = fc_params['old_fc_name']
    if 'end_status' in fc_params.keys():
        fc_params['end_status'][old_fc_name] = False
    return params


def h8(params):
    params = pop_old_thread(params)
    params = h5(params=params)
    return params


def h9(params):
    params['console']['send_string'] = 'find / -iname "*injected*"'
    params['console']['format'] = 'str'
    params['console']['wait'] = 10
    return params


def h10(params):
    params['flowchart']['exec_steps'] = 99
    params['flowchart']['use_lock'] = True
    params['flowchart']['reset_after_exe'] = True
    return params


def h11(params):
    params['wvt']['template_path'] = 'reports/template_report.xlsx'
    params = read_template_ci(params=params)
    return params


def h12(params):
    logger = params['log']['logger']
    echo_string = params['console']['echo_string']
    logger.info('ls的回显:\n{}'.format(echo_string))
    echo_string = '\r\n'.join([line for line in echo_string.split('\r\n') if not path_whitelist(line, params)])
    logger.info('过滤白名单路径后的回显:\n{}'.format(echo_string))
    results = []
    for i_fn in params['wvt']['payload_list']:
        result = {True: 'FAIL', False: 'PASS'}[i_fn in echo_string]
        # logger.info('载荷:{} 通过?:{}'.format(i_fn, result))
        results.append(result)
    data_src_dict = {
        'results': results,
        'api': [item['api'] for item in params['wvt']['testcases']],
        'cmd': [item['cmd'] for item in params['wvt']['testcases']],
        'method': [item['method'] for item in params['wvt']['testcases']],
        'payloads': [item['payload'] for item in params['wvt']['testcases']],
        'injected': [i_fn for i_fn in params['wvt']['payload_list']]
    }
    params['excel']['data_src_dict'] = data_src_dict
    params['excel']['save_path'] = params['wvt']['save_path']
    return params


def h13(params):
    params['wvt']['testcase_path'] = 'reports/payloads.xlsx'
    # params['wvt']['testcase_path'] = 'reports/payloads_test.xlsx'
    params = read_testcases_ci(params=params)
    return params


def h14(params):
    params['wvt']['template_path'] = 'reports/template_testcases.xlsx'
    params = read_template_ci(params=params)
    return params


def h15(params):
    # params['wvt']['testcase_path'] = 'reports/testcases.xlsx'
    params['wvt']['testcase_path'] = 'reports/testcases_lite.xlsx'
    # params['wvt']['testcase_path'] = 'reports/testcases_test.xlsx'
    params = read_testcases_ci(params=params)
    return params


def h16(params):
    exception = params['console']['exception']
    if exception is not None:
        params['if_switch'] = True
    else:
        params['if_switch'] = False
    return params


def h17(params):
    return params


def pop_old_thread(params):
    oldest_thread = params['thread_pool'][0]
    if 'thread_timeout' in params.keys():
        thread_timeout = params['thread_timeout']
    else:
        thread_timeout = None
    oldest_thread['thread_obj'].join(timeout=thread_timeout)
    kill_thread(thread=oldest_thread['thread_obj'])
    params['thread_pool'].pop(0)
    return params


def walk_cmd_dict(cmd_dict, dont_swap=None):
    if dont_swap is None:
        dont_swap = []
    index_list = []
    iter_list = []
    if len(dont_swap) > 0:
        dont_swap_ = dont_swap.pop(0)
    else:
        dont_swap_ = []
    if isinstance(cmd_dict, dict):
        iter_list = list(cmd_dict.keys())
    elif isinstance(cmd_dict, list):
        for i in range(len(cmd_dict)):
            iter_list.append(i)
    elif isinstance(cmd_dict, str):
        return [[None]]
    for key in iter_list:
        if type(cmd_dict[key]) in [dict, list, str] and key not in dont_swap_:
            index_prefix = [key]
            index_postfix_list = walk_cmd_dict(cmd_dict=cmd_dict[key], dont_swap=dont_swap)
            for index_postfix in index_postfix_list:
                index_list.append(index_prefix + index_postfix)
    return index_list


def set_cmd_dict(cmd_dict, index_list, value):
    key = index_list.pop(0)
    key_next = index_list[0]
    if key_next is not None:
        set_cmd_dict(cmd_dict[key], index_list, value)
    else:
        cmd_dict[key] = value


def path_whitelist(line, params):
    whitelist = params['wvt']['path_whitelist']
    for path in whitelist:
        if path in line:
            print('{}的路径在白名单中，属于正常功能产生'.format(line))
            return True
    return False


def read_template_ci(params):
    wvt_params = params['wvt']
    template_path = wvt_params['template_path']
    if 'excel' not in params.keys():
        params['excel'] = {}
    params['excel']['template_path'] = template_path
    return params


def read_testcases_ci(params):
    wvt_params = params['wvt']
    testcase_path = wvt_params['testcase_path']
    params['excel']['testcase_path'] = testcase_path
    return params


if __name__ == '__main__':
    print('Done')
