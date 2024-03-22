import datetime
import json
import random
import string
import time

from kill_thread import kill_thread


def h0(params):
    params = read_template_ci(params=params)
    return params


def h13(params):
    params['wvt']['testcase_path'] = 'reports/payloads.xlsx'
    params = read_testcases_ci(params=params)
    return params


def h14(params):
    params['wvt']['template_path'] = 'reports/template_testcases.xlsx'
    params = read_template_ci(params=params)
    return params


def h15(params):
    params['wvt']['testcase_path'] = 'reports/testcases.xlsx'
    # params['wvt']['testcase_path'] = 'reports/testcases_lite.xlsx'
    params = read_testcases_ci(params=params)
    return params


def h1(params):
    if 'console' not in params.keys():
        params['console'] = {}
    params['console'] = {
        'console_type': 'ssh',
        'dut_ip': params['wvt']['dut_ip'],
        'ssh_pass': params['wvt']['ssh_pass']
    }
    return params


def h2(params):
    all_cases = []
    # 这逼玩意就是等待执行的用例队列
    case_params = params['excel']['case_params']
    api = case_params['api']
    cmd = case_params['cmd']
    method_ = case_params['method']
    payloads = case_params['payloads']
    for i in range(len(api)):
        for j in range(len(payloads)):
            case = {'api': api[i], 'cmd': cmd[i], 'method': method_[i], 'payload': payloads[j]}
            all_cases.append(case)
    params['wvt']['testcases'] = all_cases
    params['wvt']['queue'] = all_cases.copy()
    if 'eweb' not in params.keys():
        params['eweb'] = {}
    params['eweb']['ip'] = params['wvt']['dut_ip']
    params['eweb']['pass'] = params['wvt']['eweb_pass']
    return params


def h3(params):
    queue = params['wvt']['queue']
    if len(queue) > 0:
        params['if_switch'] = True
    else:
        params['if_switch'] = False
    return params


def h4(params):
    tp_size = params['wvt']['tp_size']
    if 'slowdown_after' in params['wvt'].keys():
        tested_count = len(params['wvt']['testcases']) - len(params['wvt']['queue'])
        if tested_count >= params['wvt']['slowdown_after']:
            tp_size = 1
            print('特殊用例，取消并发请求')
    thread_pool = params['thread_pool']
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
    thread_pool = params['thread_pool']
    oldest_thread = thread_pool.pop(0)
    if 'thread_timeout' in params.keys():
        thread_timeout = params['thread_timeout']
    else:
        thread_timeout = None
    oldest_thread['thread_obj'].join(timeout=thread_timeout)
    kill_thread(thread=oldest_thread['thread_obj'])
    params = h4(params=params)
    return params


def h7(params):
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
    params['wvt']['injected_cmd'] = cmd_dict
    params['wvt']['injected_api'] = next_case['api']
    params['wvt']['inject_method'] = next_case['method']
    if 'wait_per_injection' in params['wvt'].keys():
        time.sleep(params['wvt']['wait_per_injection'])
    return params


def h8(params):
    # todo: add a timeout killer or force stopper
    thread_pool = params['thread_pool']
    oldest_thread = thread_pool.pop(0)
    oldest_thread['thread_obj'].join()
    params = h5(params=params)
    return params


def h9(params):
    # params['console']['send_string'] = 'cd /root\nls\nrm /root/*'
    params['console']['send_string'] = 'cd /root\nls'
    params['console']['format'] = 'str'
    params['console']['wait'] = 10
    return params


def h10(params):
    return params


def h11(params):
    params['wvt']['template_path'] = 'reports/template_report.xlsx'
    params = read_template_ci(params=params)
    return params


def h12(params):
    echo_string = params['console']['echo_string']
    print('ls的回显:\n{}'.format(echo_string))
    results = []
    for i_fn in params['wvt']['payload_list']:
        result = {True: 'FAIL', False: 'PASS'}[i_fn in echo_string]
        print('载荷:{} 通过?:{}'.format(i_fn, result))
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


def h16(params):
    exception = params['console']['exception']
    if exception is not None:
        params['if_switch'] = True
    else:
        params['if_switch'] = False
    return params


def h17(params):
    return params


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
