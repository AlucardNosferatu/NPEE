import time

from selenium.common import NoSuchElementException

from modules.web_api import web_start, web_goto, web_find, web_click, web_find_by_xpath, web_input_compact

page_types = [
    'unsafe https',
    'login',
    'scan list',
    'search result',
    'scan detail',
    'report export',
    'select template',
    'create scan'
]


def process_live_page(func_after_found, params, xpath):
    found = False
    dt_index = 0
    while not found:
        if dt_index >= 1024:
            dt_index = 0
        try:
            found_obj = web_find_by_xpath(params=params, xpath=xpath.format(dt_index))
            if type(found_obj) is not NoSuchElementException:
                params = func_after_found(p=params, f_obj=found_obj)
                found = True
            else:
                dt_index += 1
        except Exception as e:
            _ = e
    return params


def click_obj(p, f_obj):
    p['web'].__setitem__('click_obj', f_obj)
    p = web_click(params=p)
    return p


def nessus_summary_action(params, status, msg, page):
    params['nessus'].__setitem__('status', status)
    params['nessus'].__setitem__('msg', msg)
    params['nessus'].__setitem__('page', page)
    return params


def nessus_login(params):
    params = web_start(params=params)
    params['web'].__setitem__('goto_url', 'https://172.28.15.253:8834/#/')
    params = web_goto(params=params)
    time.sleep(5)
    if 'nessus' not in params.keys():
        params['nessus'] = {}
    username = web_find_by_xpath(params=params, xpath='/html/body/div[1]/form/div[1]/input')
    if type(username) is not NoSuchElementException:
        params = web_input_compact(params=params, input_obj=username, input_text='lanjx@ruijie.com.cn')
        password = web_find_by_xpath(params=params, xpath='/html/body/div[1]/form/div[2]/input')
        if type(password) is not NoSuchElementException:
            params = web_input_compact(params=params, input_obj=password, input_text='Ruijie.123')
            sign_in = web_find_by_xpath(params=params, xpath='/html/body/div[1]/form/button')
            if type(sign_in) is not NoSuchElementException:
                params['web'].__setitem__('click_obj', sign_in)
                params = web_click(params=params)
                time.sleep(20)
                params = nessus_summary_action(params=params, status=True, msg=None, page='scan list')
            else:
                params = nessus_summary_action(
                    params=params, status=False, msg="Cannot find 'Sign In' button.", page='login'
                )
        else:
            params = nessus_summary_action(
                params=params, status=False, msg="Cannot find password inputbox.", page='login'
            )
    else:
        params = nessus_summary_action(
            params=params, status=False, msg="Cannot find username inputbox.", page='login'
        )
    return params


def nessus_select_folder(params):
    _ = params
    raise NotImplementedError('My Scans is the default folder.')
    # noinspection PyUnreachableCode
    return params


def nessus_find(params):
    assert params['nessus']['page'] in ['scan list', 'search result']
    scan_name = params['nessus']['scan_name']
    del params['nessus']['scan_name']
    # noinspection SpellCheckingInspection
    search_box = web_find_by_xpath(params=params, xpath='//*[@id="searchbox"]/input')
    if type(search_box) is not NoSuchElementException:
        params = web_input_compact(params=params, input_obj=search_box, input_text=scan_name)
        time.sleep(5)
        params = nessus_summary_action(params=params, status=True, msg=None, page='search result')
    else:
        params = nessus_summary_action(params=params, status=False, msg='Cannot find search box', page='scan list')
    return params


def nessus_get_status(params):
    def parse_status(p, f_obj):
        status = f_obj.get_attribute(name='class')
        p['nessus']['scan_status'] = status.replace('glyphicons scan-status ', '').replace(' add-tip', '')
        return p

    assert params['nessus']['page'] == 'search result'
    xpath = '//*[@id="DataTables_Table_{}"]/thead/tr/th[7]'
    func_after_found = click_obj

    params = process_live_page(func_after_found=func_after_found, params=params, xpath=xpath)

    xpath = '//*[@id="DataTables_Table_{}"]/tbody/tr/td[6]/i'
    func_after_found = parse_status

    params = process_live_page(func_after_found=func_after_found, params=params, xpath=xpath)

    params = nessus_summary_action(params=params, status=True, msg=None, page='search result')
    return params


def nessus_start_pause(params):
    assert params['nessus']['page'] == 'search result'
    xpath = '//*[@id="DataTables_Table_{}"]/tbody/tr[1]/td[9]/i'
    func_after_found = click_obj

    params = process_live_page(func_after_found=func_after_found, params=params, xpath=xpath)

    time.sleep(10)
    params = nessus_summary_action(params=params, status=True, msg=None, page='search result')
    params = nessus_get_status(params=params)
    return params


def nessus_delete_stop(params):
    assert params['nessus']['page'] == 'search result'
    xpath = '//*[@id="DataTables_Table_{}"]/tbody/tr[1]/td[10]/i'
    func_after_found = click_obj

    params = process_live_page(func_after_found=func_after_found, params=params, xpath=xpath)

    time.sleep(10)
    params = nessus_summary_action(params=params, status=True, msg=None, page='search result')
    # p = nessus_get_status(p=p)
    # todo: delete operation will stuck get_status
    return params


def nessus_export(params):
    assert params['nessus']['page'] == 'search result'
    xpath = '//*[@id="DataTables_Table_{}"]/tbody/tr/td[3]'
    func_after_found = click_obj

    params = process_live_page(func_after_found=func_after_found, params=params, xpath=xpath)

    time.sleep(5)
    params['web'].__setitem__('find_by', 'id')
    # noinspection SpellCheckingInspection
    params['web'].__setitem__('find_value', 'generate-scan-report')
    params = web_find(params=params)
    report = params['web']['find_result']
    del params['web']['find_result']
    if type(report) is not NoSuchElementException:
        params['web'].__setitem__('click_obj', report)
        params = web_click(params=params)
        time.sleep(5)
        format_html = web_find_by_xpath(
            params=params,
            xpath='//*[@id="modal-inside"]/div[1]/div[2]/div[1]/div/div[1]'
        )
        if type(format_html) is not NoSuchElementException:
            params['web'].__setitem__('click_obj', format_html)
            params = web_click(params=params)
            time.sleep(5)
            vul_operation = web_find_by_xpath(params=params, xpath='//*[@id="templates"]/option[16]')
            if type(vul_operation) is not NoSuchElementException:
                vul_operation.click()
                time.sleep(5)
                params['web'].__setitem__('find_by', 'id')
                # noinspection SpellCheckingInspection
                params['web'].__setitem__('find_value', 'report-save')
                params = web_find(params=params)
                report_save = params['web']['find_result']
                del params['web']['find_result']
                if type(report_save) is not NoSuchElementException:
                    params['web'].__setitem__('click_obj', report_save)
                    params = web_click(params=params)
                    time.sleep(5)
                    back = web_find_by_xpath(params=params, xpath='//*[@id="titlebar"]/div/a')
                    if type(back) is not NoSuchElementException:
                        params['web'].__setitem__('click_obj', back)
                        params = web_click(params=params)
                        time.sleep(10)
                        params = nessus_summary_action(params=params, status=True, msg=None, page='scan list')
                    else:
                        params = nessus_summary_action(
                            params=params,
                            status=False,
                            msg="Cannot find 'Back to [folder_name]' link.",
                            page='scan detail'
                        )
                else:
                    params = nessus_summary_action(
                        params=params,
                        status=False,
                        msg="Cannot find 'Generate Report' button.",
                        page='report export'
                    )
            else:
                params = nessus_summary_action(
                    params=params,
                    status=False,
                    msg="Cannot find 'vul_operation' option for report export.",
                    page='report export'
                )
        else:
            params = nessus_summary_action(
                params=params,
                status=False,
                msg="Cannot find 'HTML' option for report export format.",
                page='report export'
            )
    else:
        params = nessus_summary_action(
            params=params,
            status=False,
            msg="Cannot find 'Report' button in scan detail page.",
            page='scan detail'
        )

    return params


def nessus_new_scan(params):
    assert params['nessus']['page'] in ['scan list', 'search result']
    scan_name = params['nessus']['scan_name']
    del params['nessus']['scan_name']
    scan_hosts = params['nessus']['scan_hosts']
    del params['nessus']['scan_hosts']

    params['web'].__setitem__('find_by', 'id')
    # noinspection SpellCheckingInspection
    params['web'].__setitem__('find_value', 'new-scan')
    params = web_find(params=params)
    new_scan = params['web']['find_result']
    del params['web']['find_result']
    if type(new_scan) is not NoSuchElementException:
        params['web'].__setitem__('click_obj', new_scan)
        params = web_click(params=params)
        time.sleep(5)
        advanced_scan = web_find_by_xpath(params=params, xpath='//*[@id="content"]/section/div[1]/div[2]/div[2]/a[2]')
        if type(advanced_scan) is not NoSuchElementException:
            params['web'].__setitem__('click_obj', advanced_scan)
            params = web_click(params=params)
            time.sleep(10)
            scan_name_inputbox = web_find_by_xpath(
                params=params,
                xpath='//*[@id="editor-tab-view"]/div/div[1]/section/div[1]/div[1]/div[1]/div[1]/div/input'
            )
            if type(scan_name_inputbox) is not NoSuchElementException:
                params = web_input_compact(params=params, input_obj=scan_name_inputbox, input_text=scan_name)
                time.sleep(1)
                scan_hosts_inputbox = web_find_by_xpath(
                    params=params,
                    xpath='//*[@id="editor-tab-view"]/div/div[1]/section/div[1]/div[1]/div[1]/div[5]/div/textarea'
                )
                if type(scan_hosts_inputbox) is not NoSuchElementException:
                    params = web_input_compact(params=params, input_obj=scan_hosts_inputbox, input_text=scan_hosts)
                    description = web_find_by_xpath(
                        params=params,
                        xpath='//*[@id="editor-tab-view"]/div/div[1]/section/div[1]/div[1]/div[1]/div[2]/div/textarea'
                    )
                    if type(description) is not NoSuchElementException:
                        params = web_input_compact(params=params, input_obj=description, input_text='')
                        time.sleep(1)
                        save_scan = web_find_by_xpath(
                            params=params,
                            xpath='//*[@id="content"]/section/form/div[2]/span'
                        )
                        if type(save_scan) is not NoSuchElementException:
                            params['web'].__setitem__('click_obj', save_scan)
                            params = web_click(params=params)
                            time.sleep(20)
                            params = nessus_summary_action(params=params, status=True, msg=None, page='scan list')
                        else:
                            params = nessus_summary_action(
                                params=params,
                                status=False,
                                msg="Cannot find 'Save' button for saving scan.",
                                page='create scan'
                            )
                    else:
                        params = nessus_summary_action(
                            params=params,
                            status=False,
                            msg="Cannot find 'Description' inputbox.",
                            page='create scan'
                        )
                else:
                    params = nessus_summary_action(
                        params=params,
                        status=False,
                        msg="Cannot find 'Targets' inputbox.",
                        page='create scan'
                    )
            else:
                params = nessus_summary_action(
                    params=params,
                    status=False,
                    msg="Cannot find 'Name' inputbox.",
                    page='create scan'
                )
        else:
            params = nessus_summary_action(
                params=params,
                status=False,
                msg="Cannot find 'Advanced Scan' template.",
                page='select template'
            )
    else:
        params = nessus_summary_action(
            params=params,
            status=False,
            msg="Cannot find '+New Scan' button.",
            page='scan list'
        )
    return params


def nessus_back2list(params):
    if params['nessus']['page'] in ['search result', 'scan list']:
        params = nessus_summary_action(params=params, status=True, msg=None, page='scan list')
    elif params['nessus']['page'] in ['unsafe https', 'login']:
        params = nessus_login(params=params)
    elif params['nessus']['page'] in ['scan detail', 'select template']:
        back2list = web_find_by_xpath(params=params, xpath='//*[@id="titlebar"]/div/a')
        if type(back2list) is not NoSuchElementException:
            params['web'].__setitem__('click_obj', back2list)
            params = web_click(params=params)
            time.sleep(10)
            params = nessus_summary_action(params=params, status=True, msg=None, page='scan list')
        else:
            params = nessus_summary_action(
                params=params,
                status=False,
                msg="Cannot find 'Back to Scans/[folder_name]' link.",
                page=params['nessus']['page']
            )
    elif params['nessus']['page'] == 'create scan':
        back2templates = web_find_by_xpath(params=params, xpath='//*[@id="titlebar"]/div[1]/a')
        if type(back2templates) is not NoSuchElementException:
            params['web'].__setitem__('click_obj', back2templates)
            params = web_click(params=params)
            time.sleep(10)
            params = nessus_summary_action(params=params, status=True, msg=None, page='select template')
            params = nessus_back2list(params=params)
        else:
            params = nessus_summary_action(
                params=params,
                status=False,
                msg="Cannot find 'Back to Scan Templates' link.",
                page=params['nessus']['page']
            )
    elif params['nessus']['page'] == 'report export':
        back2detail = web_find_by_xpath(params=params, xpath='//*[@id="modal-inside"]/div[1]/div[3]/a[2]')
        if type(back2detail) is not NoSuchElementException:
            params['web'].__setitem__('click_obj', back2detail)
            params = web_click(params=params)
            time.sleep(10)
            params = nessus_summary_action(params=params, status=True, msg=None, page='scan detail')
            params = nessus_back2list(params=params)
        else:
            params = nessus_summary_action(
                params=params,
                status=False,
                msg="Cannot find 'Cancel' button.",
                page=params['nessus']['page']
            )
    else:
        params = nessus_summary_action(
            params=params,
            status=False,
            msg='Cannot handle page status:{}'.format(params['nessus']['page']),
            page=params['nessus']['page']
        )
    return params


if __name__ == '__main__':
    params_ = {}
    params_ = nessus_login(params=params_)
    params_['nessus'] = {
        'scan_name': 'EW1300G-R229',
        'scan_hosts': '127.0.0.1'
    }
    params_ = nessus_new_scan(params=params_)
    params_['nessus'] = {
        'scan_name': 'EW1300G-R229'
    }
    params_ = nessus_find(params=params_)
    params_ = nessus_get_status(params=params_)
    params_ = nessus_export(params=params_)
    params_['nessus'] = {
        'scan_name': 'EW1300G-R229'
    }
    params_ = nessus_find(params=params_)
    params_ = nessus_delete_stop(params=params_)
    print('Done')
