import os
import time

import uiautomator2 as u2

netsh_prefix_str = 'netsh interface portproxy add v4tov4'


def android_forward_device(params):
    forward_device_params = params['android']
    uid = forward_device_params['uid']
    del forward_device_params['uid']
    device_port = forward_device_params['device_port']
    external_address = forward_device_params['external_address']
    if 'internal_port' in forward_device_params.keys():
        internal_port = forward_device_params['internal_port']
    else:
        internal_port = device_port
    if 'external_port' in forward_device_params.keys():
        external_port = forward_device_params['external_port']
    else:
        external_port = internal_port
    os.system('adb -s {} tcpip {}'.format(uid, device_port))
    time.sleep(10)
    os.system('adb -s {} forward tcp:{} tcp:{}'.format(uid, internal_port, device_port))
    os.system(
        '{} listenaddress={} listenport={} connectaddress=127.0.0.1 connectport={}'.format(
            netsh_prefix_str, external_address, external_port, internal_port
        )
    )
    proxy_uid = '{}:{}'.format(external_address, external_port)
    forward_device_params.__setitem__('proxy_uid', proxy_uid)
    return params


def android_connect_device(params):
    connect_device_params = params['android']
    uid = connect_device_params['uid']
    del connect_device_params['uid']
    os.system('adb connect {}'.format(uid))
    connect_device_params.__setitem__('connected_uid', uid)
    return params


def android_init_device(params):
    init_device_params = params['android']
    uid = init_device_params['uid']
    del init_device_params['uid']
    u2_obj = u2.connect(uid)
    u2_obj.uiautomator.start()
    init_device_params.__setitem__('u2_obj', u2_obj)
    return params


def android_app_control(params):
    app_control_params = params['android']
    u2_obj: u2.Device = app_control_params['u2_obj']
    app_action = app_control_params['app_action']
    del app_control_params['app_action']
    if app_action == 'show':
        current_app = u2_obj.app_current()
        app_control_params.__setitem__('current_app', current_app)
        pid = -1
    elif app_action == 'install':
        apk_path = app_control_params['apk_path']
        del app_control_params['apk_path']
        u2_obj.app_install(data=apk_path)
        pid = -1
    else:
        app_name = app_control_params['app_name']
        del app_control_params['app_name']
        if app_action == 'uninstall':
            pid = u2_obj.app_uninstall(package_name=app_name)
            if pid:
                pid = -1
            else:
                pid = 0
        elif app_action == 'start':
            u2_obj.app_start(package_name=app_name)
            pid = u2_obj.app_wait(package_name=app_name)
        elif app_action == 'restart':
            u2_obj.app_stop(package_name=app_name)
            time.sleep(1)
            u2_obj.app_start(package_name=app_name)
            pid = u2_obj.app_wait(package_name=app_name)
        elif app_action == 'stop':
            u2_obj.app_stop(package_name=app_name)
            pid = -1
        elif app_action == 'clear':
            u2_obj.app_stop(package_name=app_name)
            u2_obj.app_clear(package_name=app_name)
            pid = -1
        elif app_action == 'stop_all':
            if 'excludes' in app_control_params.keys():
                excludes = app_control_params['excludes']
                del app_control_params['excludes']
            else:
                excludes = []
            stopped = u2_obj.app_stop_all(excludes=excludes)
            app_control_params.__setitem__('stopped', stopped)
            pid = -1
        else:
            error_prompt = 'Only {} are supported.'
            error_prompt = error_prompt.format("'install', {}")
            error_prompt = error_prompt.format("'uninstall', {}")
            error_prompt = error_prompt.format("'start', {}")
            error_prompt = error_prompt.format("'restart', {}")
            error_prompt = error_prompt.format("'stop', {}")
            error_prompt = error_prompt.format("'stop_all' {}")
            error_prompt = error_prompt.format("and 'clear'")
            raise ValueError(error_prompt)
    if pid != 0:
        status = True
    else:
        status = False
    app_control_params.__setitem__('status', status)
    return params


def android_get_element(params):
    get_element_params = params['android']
    u2_obj: u2.Device = get_element_params['u2_obj']
    by = get_element_params['by']
    del get_element_params['by']
    value = get_element_params['value']
    del get_element_params['value']
    if by == 'xpath':
        results = u2_obj.xpath(xpath=value)
    elif by == 'class':
        path = value.split('||')[0]
        index = int(value.split('||')[1])
        results = u2_obj(className=path)[index]
    else:
        raise ValueError("Only 'xpath' and 'class' are supported.")
    get_element_params.__setitem__('found', results)
    return params


def android_interact_element(params):
    interact_element_params = params['android']
    element: u2.xpath.XPathSelector = interact_element_params['element']
    del interact_element_params['element']
    element_action = interact_element_params['element_action']
    # del interact_element_params['element_action']
    if element_action in ['click', 'input']:
        element.click()
        if element_action == 'input':
            u2_obj: u2.Device = interact_element_params['u2_obj']
            input_text = interact_element_params['input_text']
            del interact_element_params['input_text']
            u2_obj.send_keys(text=input_text, clear=True)
    elif element_action == 'long_click':
        element.long_click()
    elif element_action == 'read':
        read_text = element.get_text()
        interact_element_params.__setitem__('read_text', read_text)
    else:
        raise ValueError("Only 'click', 'input', 'long_click' and 'read' are supported.")
    return params


def android_interact_device(params):
    interact_device_params = params['android']
    u2_obj: u2.Device = interact_device_params['u2_obj']
    device_action = interact_device_params['device_action']
    # del interact_device_params['device_action']
    if device_action == 'unlock':
        u2_obj.unlock()
    elif device_action == 'screen_on':
        u2_obj.screen_on()
    elif device_action == 'screen_off':
        u2_obj.screen_off()
    elif device_action == 'screenshot':
        if 'screenshot_filepath' in interact_device_params.keys():
            screenshot_filepath = interact_device_params['screenshot_filepath']
            del interact_device_params['screenshot_filepath']
            u2_obj.screenshot(filename=screenshot_filepath)
        else:
            img_array = u2_obj.screenshot(format="opencv")
            if 'cv' not in params:
                params['cv'] = {}
            params['cv']['img_array'] = img_array
    elif device_action == 'double_click':
        coordinate = interact_device_params['coordinate']
        del interact_device_params['coordinate']
        # coordinate = {'x': 0, 'y': 0}
        u2_obj.double_click(x=coordinate['x'], y=coordinate['y'])
    elif device_action in ['drag', 'swipe']:
        coordinate_1 = interact_device_params['coordinate_1']
        del interact_device_params['coordinate_1']
        coordinate_2 = interact_device_params['coordinate_2']
        del interact_device_params['coordinate_2']
        if device_action == 'drag':
            u2_obj.drag(sx=coordinate_1['x'], sy=coordinate_1['y'], ex=coordinate_2['x'], ey=coordinate_2['y'])
        else:
            u2_obj.swipe(fx=coordinate_1['x'], fy=coordinate_1['y'], tx=coordinate_2['x'], ty=coordinate_2['y'])
    else:
        error_prompt = 'Only {} are supported.'
        error_prompt = error_prompt.format("'unlock', {}")
        error_prompt = error_prompt.format("'screen_on', {}")
        error_prompt = error_prompt.format("'screen_off', {}")
        error_prompt = error_prompt.format("'screenshot', {}")
        error_prompt = error_prompt.format("'double_click', {}")
        error_prompt = error_prompt.format("'drag' {}")
        error_prompt = error_prompt.format("and 'swipe'")
        raise ValueError(error_prompt)
    return params


def android_add_watcher(params):
    add_watcher_params = params['android']
    u2_obj: u2.Device = add_watcher_params['u2_obj']

    watcher_name = add_watcher_params['watcher_name']
    del add_watcher_params['watcher_name']
    watcher = u2_obj.watcher(name=watcher_name)

    watcher_xpath = add_watcher_params['watcher_xpath']
    del add_watcher_params['watcher_xpath']
    watcher = watcher.when(xpath=watcher_xpath)

    watcher_action = add_watcher_params['watcher_action']
    del add_watcher_params['watcher_action']
    if watcher_action == 'click':
        watcher.click()
    elif watcher_action == 'press':
        watcher_press_key = add_watcher_params['watcher_press_key']
        del add_watcher_params['watcher_press_key']
        watcher.press(key=watcher_press_key)
    else:
        error_prompt = 'Only {} are supported.'
        error_prompt = error_prompt.format("'click', {}")
        error_prompt = error_prompt.format("and 'press'")
        raise ValueError(error_prompt)
    if 'watchers' not in add_watcher_params.keys():
        add_watcher_params.__setitem__('watchers', [])
    add_watcher_params['watchers'].append(watcher_name)
    return params


def android_remove_watcher(params):
    remove_watcher_params = params['android']
    u2_obj: u2.Device = remove_watcher_params['u2_obj']
    watcher_name = remove_watcher_params['watcher_name']
    del remove_watcher_params['watcher_name']
    u2_obj.watcher.remove(name=watcher_name)
    if 'watchers' not in remove_watcher_params.keys():
        remove_watcher_params.__setitem__('watchers', [])
    else:
        while watcher_name in remove_watcher_params['watchers']:
            remove_watcher_params['watchers'].remove(watcher_name)
    return params


def android_reset_watcher(params):
    reset_watcher_params = params['android']
    u2_obj: u2.Device = reset_watcher_params['u2_obj']
    u2_obj.watcher.reset()
    if 'watchers' not in reset_watcher_params.keys():
        reset_watcher_params.__setitem__('watchers', [])
    else:
        while len(reset_watcher_params['watchers']) > 0:
            reset_watcher_params['watchers'].clear()
    return params


if __name__ == '__main__':
    params_ = {
        'android': {
            'uid': 'OZRCWWCYIFDMKFYL'
        }
    }
    params_ = android_init_device(params=params_)
    params_['android']['device_action'] = 'screenshot'
    params_['android']['screenshot_filepath'] = 'reports/WZRY.png'
    params_ = android_interact_device(params=params_)
    print('Done')
