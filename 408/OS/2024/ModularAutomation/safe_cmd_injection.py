# import cProfile
import os
# import pstats

from core.flow_chart import FlowChart
from modules.logger import log_handler_init, log_logger_init
from modules.webhook_api import webhook_send

from safe_common_config import scan_host, target_name, eweb_pass, ssh_pass

if __name__ == '__main__':
    # profiler = cProfile.Profile()
    # profiler.enable()
    ready = False
    wait_after_reboot = 60
    ping_times = 5
    tp_size = 8
    rq_size = 16
    wait_per_injection = 0.25
    repost_retry = 5
    while not ready:
        try:
            params_input = input('格式:IP地址#型号#EWEB密码#SSH密码\n')
            if params_input == 'USE_HARDCODED':
                ready = True
            else:
                params_input = params_input.split('#')
                scan_host = params_input[0]
                target_name = params_input[1]
                eweb_pass = params_input[2]
                ssh_pass = params_input[3]
                print('IP地址:{}'.format(scan_host))
                print('型号:{}'.format(target_name))
                print('EWEB密码:{}'.format(eweb_pass))
                print('SSH密码:{}'.format(ssh_pass))
                if len(params_input) > 4:
                    for extra_param in params_input[4:]:
                        if extra_param.startswith('$WAR:'):
                            wait_after_reboot = float(extra_param.replace('$WAR:', ''))
                            print('【$WAR:】重启后等待时长:{}'.format(wait_after_reboot))
                        elif extra_param.startswith('$PT:'):
                            ping_times = int(extra_param.replace('$PT:', ''))
                            print('【$PT:】重启后PING次数:{}'.format(ping_times))
                        elif extra_param.startswith('$TPS:'):
                            tp_size = int(extra_param.replace('$TPS:', ''))
                            print('【$TPS:】执行线程池大小:{}'.format(tp_size))
                        elif extra_param.startswith('$RQS:'):
                            rq_size = int(extra_param.replace('$RQS:', ''))
                            print('【$RQS:】请求队列大小:{}'.format(rq_size))
                        elif extra_param.startswith('$WPI:'):
                            wait_per_injection = float(extra_param.replace('$WPI:', ''))
                            print('【$WPI:】请求间隔时长:{}'.format(wait_per_injection))
                        elif extra_param.startswith('$RR:'):
                            repost_retry = int(extra_param.replace('$RR:', ''))
                            print('【$RR:】请求重试次数:{}'.format(repost_retry))
                confirm = input('确认无误?(Y)')
                if confirm == 'Y':
                    ready = True
        except BaseException as e:
            print('解析输入参数时发生错误:{}'.format(repr(e)))
    params = {
        'wvt': {
            'wait_after_reboot': wait_after_reboot,
            'ping_times': ping_times,
            'checkpoint_path': 'reports/checkpoint-{}.pkl'.format(target_name),
            'dut_ip': scan_host,
            'ssh_pass': ssh_pass,
            'save_path': 'reports/{}-命令注入.xlsx'.format(target_name),
            'eweb_pass': eweb_pass,
            'tp_size': tp_size,
            'rq_size': rq_size,
            'payload_list': [],
            # 'slowdown_after': 66,
            'template_path': 'reports/template_payloads.xlsx',
            'wait_per_injection': wait_per_injection,
            'repost_retry': repost_retry,
            'path_whitelist': [
                '/tmp/enetCap/single/modules',
                '/etc/rg_config/global',
                '/etc/rg_config/single'
            ]
        }
    }
    fc = FlowChart(prerequisite=params)
    fc.load_map(hook_script='cmd_injection.py', map_json='命令注入测试.pos')
    # todo: makeshift patch
    fc.params_bus['log'] = {'logger_name': 'cmd_injection', 'log_backup_count': 8192}
    fc.params_bus = log_logger_init(params=fc.params_bus)
    fc.params_bus = log_handler_init(params=fc.params_bus)
    end = False
    fc.params_bus['webhook'] = {
        'webhook_url': 'https://open.feishu.cn/open-apis/bot/v2/hook/49487983-e106-49c8-a527-4b8a4dfeddf5',
        'send_string': '{}的命令注入测试开始'.format(target_name)
    }
    fc.params_bus = webhook_send(params=fc.params_bus)
    while not end:
        end = fc.run_step()
    fc.params_bus['webhook']['send_string'] = '{}的命令注入测试已完成'.format(target_name)
    fc.params_bus = webhook_send(params=fc.params_bus)
    # profiler.disable()
    # pstats.Stats(
    #     profiler, stream=open('reports/性能分析-命令注入.txt', 'w')
    # ).sort_stats(pstats.SortKey.CUMULATIVE).print_stats(.3)
    os.abort()
