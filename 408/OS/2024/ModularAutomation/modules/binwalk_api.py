import os
import subprocess

fail_if_exists = ['bin', 'controller', 'dev', 'etc', 'lib', 'lib64', 'mnt', 'model',
                  'overlay', 'proc', 'rom', 'root', 'sbin', 'sys', 'tmp', 'usr', 'var', 'www']


def binwalk_scan(params):
    binwalk_params = params['binwalk']
    args = binwalk_params['args']
    target_file = binwalk_params['target_file']
    target_folder = binwalk_params['target_folder']
    try:
        scan_output = subprocess.check_output('binwalk {} {}'.format(args, os.path.join(target_folder, target_file)))
        try:
            scan_output = scan_output.decode('utf-8')
        except UnicodeDecodeError:
            scan_output = scan_output.decode('gbk')
        binwalk_params['scan_output'] = scan_output
        binwalk_params['exception'] = None
    except Exception as e:
        print('binwalk解析文件内容时发生错误:{}'.format(repr(e)))
        binwalk_params['scan_output'] = None
        binwalk_params['exception'] = e
    return params


def binwalk_check(params):
    detected = []
    try:
        binwalk_params = params['binwalk']
        target_file = binwalk_params['target_file']
        extracted = '_{}.extracted'.format(target_file)
        fail = False
        for root, dirs, _ in os.walk(extracted):
            for dir_ in dirs:
                for dead_case in fail_if_exists:
                    if dead_case == dir_:
                        warn = '检测到被解压成功的文件系统目录:{}\n位于:{}'.format(dir_, root)
                        detected.append(warn)
                        print(warn)
                        fail = True
        binwalk_params['result'] = {True: 'FAIL', False: 'PASS'}[fail]
        if binwalk_params['exception'] is None:
            binwalk_params['exception'] = None
    except Exception as e:
        print('binwalk检查解压文件时发生错误:{}'.format(repr(e)))
        binwalk_params['result'] = None
        if binwalk_params['exception'] is None:
            binwalk_params['exception'] = e
        else:
            binwalk_params['exception'] = [binwalk_params['exception'], e]
    binwalk_params['detected'] = detected
    return params
