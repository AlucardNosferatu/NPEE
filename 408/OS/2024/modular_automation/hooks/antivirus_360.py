import time


def h0(params):
    return params


def h1(params):
    if 'win_ui' not in params.keys():
        params['win_ui'] = {}
    # win_ui_params = params['win_ui']
    # work_dir = params['360epp']['work_dir']
    # win_ui_params['work_dir'] = work_dir
    return params


def h2(params):
    win_ui_params = params['win_ui']
    win_ui_params['parent'] = 'explorer'
    win_ui_params['class_name'] = 'CabinetWClass'
    return params


def h3(params):
    win_ui_params = params['win_ui']
    exception = win_ui_params['exception']
    if exception is not None:
        params['if_switch'] = True
    else:
        params['if_switch'] = False
    return params


def h4(params):
    win_ui_params = params['win_ui']
    win_ui_params['parent'] = 'window'
    win_ui_params['class_name'] = 'ShellTabWindowClass'
    return params


def h5(params):
    win_ui_params = params['win_ui']
    win_ui_params['parent'] = 'element'
    win_ui_params['class_name'] = 'DUIViewWndClassName'
    return params


def h6(params):
    win_ui_params = params['win_ui']
    win_ui_params['parent'] = 'element'
    win_ui_params['class_name'] = 'DUIListView'
    return params


def h7(params):
    win_ui_params = params['win_ui']
    win_ui_params['parent'] = 'element'
    win_ui_params['class_name'] = 'UIItemsView'
    return params


def h8(params):
    win_ui_params = params['win_ui']
    win_ui_params['parent'] = 'element'
    win_ui_params['class_name'] = 'UIGroupItem'
    win_ui_params['name'] = '文件夹'
    return params


def h9(params):
    win_ui_params = params['win_ui']
    win_ui_params['parent'] = 'element'
    win_ui_params['class_name'] = 'UIItem'
    scan_folder = params['360epp']['scan_folder']
    win_ui_params['name'] = scan_folder
    return params


def h10(params):
    win_ui_params = params['win_ui']
    win_ui_params['parent'] = 'element'
    win_ui_params['class_name'] = 'UIImage'
    win_ui_params['name'] = ''
    return params


def h11(params):
    win_ui_params = params['win_ui']
    win_ui_params['title'] = 'UI自动化'
    win_ui_params['message'] = 'UI自动化操作开始！\n请勿操作计算机！'
    params['360epp']['scan_folder_clickable'] = win_ui_params['element']
    return params


def h12(params):
    win_ui_params = params['win_ui']
    win_ui_params['click_type'] = 'right'
    win_ui_params['offset'] = {'x': 50, 'y': 10}
    scan_folder_clickable = params['360epp']['scan_folder_clickable']
    win_ui_params['element'] = scan_folder_clickable
    return params


def h13(params):
    time.sleep(5)
    win_ui_params = params['win_ui']
    win_ui_params['parent'] = 'desktop'
    win_ui_params['class_name'] = '#32768'
    return params


def h14(params):
    win_ui_params = params['win_ui']
    win_ui_params['parent'] = 'window'
    win_ui_params['name'] = '使用 360杀毒 扫描'
    return params


def h15(params):
    win_ui_params = params['win_ui']
    win_ui_params['click_type'] = 'left'
    win_ui_params['offset'] = {'x': 50, 'y': 10}
    return params


def h16(params):
    win_ui_params = params['win_ui']
    win_ui_params['title'] = 'UI自动化'
    win_ui_params['message'] = 'UI自动化操作结束！\n您可操作计算机！'
    return params


def h17(params):
    time.sleep(15)
    if 'database' not in params.keys():
        params['database'] = {}
    db_params = params['database']
    db_params['db_path'] = params['360epp']['log_path']
    db_params['db_type'] = 'sqlite'
    return params


def h18(params):
    db_params = params['database']
    read_table = params['360epp']['log_table']
    db_params['sql_code'] = 'SELECT * FROM {}'.format(read_table)
    return params


def h19(params):
    db_params = params['database']
    result_df = db_params['result_df']
    del db_params['result_df']
    last_scan = list(result_df.values[-1, :])[3:7]
    for i in range(len(last_scan)):
        last_scan[i] = last_scan[i].replace('\r', '\n')
        while '\n\n' in last_scan[i]:
            last_scan[i] = last_scan[i].replace('\n\n', '\n')
    params['360epp']['last_scan'] = '\n'.join(last_scan)
    txt_path = params['360epp']['txt_path']
    with open(txt_path, 'w') as f:
        f.writelines(params['360epp']['last_scan'])
    return params


def h20(params):
    return params
