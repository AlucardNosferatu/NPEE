def h0(params):
    # params['binwalk'] = {}
    # params['binwalk']['args'] = '-Me'
    # params['binwalk']['target_file'] = 'EW_3.0B11P258_EW5000_11151219_install.bin'
    # params['binwalk']['target_folder'] = 'D:\\RjDir\\admin_d95c8884-f44c-4529-8f3b-48d5788371c1\\Downloads\\业务文档\\安全扫描\\R258-BE50\\升级文件'
    # params['binwalk']['save_txt'] = 'reports\\BE50-隐写保密性测试.txt'
    return params


def h1(params):
    return params


def h2(params):
    exception = '测试当中发生异常？:{}'.format(params['binwalk']['exception'])
    target = '测试对象:{} 所在目录:{}'.format(params['binwalk']['target_file'], params['binwalk']['target_folder'])
    conclusion = '测试结论:{}'.format(params['binwalk']['result'])
    detected = '检测到的文件系统目录:\n{}'.format('\n'.join(params['binwalk']['detected']))
    scan_output = 'binwalk日志:\n{}'.format(params['binwalk']['scan_output'])
    report = '\n===================================\n'.join([target, exception, conclusion, detected, scan_output])
    with open(params['binwalk']['save_txt'], 'w') as f:
        f.writelines(report)
    return params
