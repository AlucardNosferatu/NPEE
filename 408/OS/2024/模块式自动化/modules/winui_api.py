import threading
import time
from tkinter import messagebox

import keyboard
import pyautogui as pyautogui
import pywinauto

mouse_lock = False
pyautogui.PAUSE = 0.00001


def lock_mouse(tgt, offset=None):
    def lock_action(tgt_, offset_=None):
        global mouse_lock
        mouse_lock = True
        pos = pyautogui.position()
        for _ in range(16):
            tgt_.set_focus()
            tgt_.move_mouse_input(absolute=False)
            pos = pyautogui.position()
        if offset_ is None:
            offset_x, offset_y = 0, 0
        else:
            offset_x, offset_y = offset_['x'], offset_['y']
        while mouse_lock:
            current_pos = pyautogui.position()
            spd_comp_x = pos[0] - current_pos[0]
            spd_comp_y = pos[1] - current_pos[1]
            comp_ratio = 0.75
            spd_comp_x = int(spd_comp_x * comp_ratio)
            spd_comp_y = int(spd_comp_y * comp_ratio)
            pyautogui.moveTo(x=pos[0] + offset_x + spd_comp_x, y=pos[1] + offset_y + spd_comp_y)

    lock_thread = threading.Thread(target=lock_action, args=(tgt, offset))
    lock_thread.start()
    print('鼠标已锁定')


def release_mouse():
    global mouse_lock
    mouse_lock = False
    print('鼠标已释放')


def anti_deadlock():
    while True:
        time.sleep(0.1)
        if keyboard.is_pressed('alt+shift+ctrl+a'):
            release_mouse()


ad_daemon = threading.Thread(target=anti_deadlock)
ad_daemon.start()


def winui_get_explorer(params):
    if 'win_ui' not in params.keys():
        params['win_ui'] = {'work_dir': r'C:\Users\16413\Downloads\Docs'}
    win_ui_params = params['win_ui']
    if 'work_dir' in win_ui_params.keys():
        work_dir = win_ui_params['work_dir']
        del win_ui_params['work_dir']
        pywinauto.Application().start(cmd_line='explorer.exe "{}"'.format(work_dir))
    explorer = pywinauto.Application(backend='uia').connect(path='explorer.exe')
    win_ui_params['explorer'] = explorer
    return params


def winui_get_desktop(params):
    if 'win_ui' not in params.keys():
        params['win_ui'] = {}
    win_ui_params = params['win_ui']
    desktop = pywinauto.Desktop(backend="uia")
    win_ui_params['desktop'] = desktop
    return params


def winui_locate_window(params):
    win_ui_params = params['win_ui']
    parent = win_ui_params['parent']
    del win_ui_params['parent']
    class_name = win_ui_params['class_name']
    del win_ui_params['class_name']
    try:
        if parent == 'explorer':
            window = win_ui_params['explorer'].window(class_name=class_name)
        elif parent == 'desktop':
            window = win_ui_params['desktop'].window(class_name=class_name)
        else:
            raise ValueError('Only explorer and desktop are allowed parent for the window!')
        win_ui_params['window'] = window
        win_ui_params['exception'] = None
    except Exception as e:
        win_ui_params['exception'] = e
    return params


def winui_capture_window(params):
    win_ui_params = params['win_ui']
    window = win_ui_params['window']
    pic_path = win_ui_params['pic_path']
    del win_ui_params['pic_path']
    try:
        window.set_focus()
        window.capture_as_image().save(pic_path)
        win_ui_params['exception'] = None
    except Exception as e:
        win_ui_params['exception'] = e
    return params


def winui_close_window(params):
    win_ui_params = params['win_ui']
    window = win_ui_params['window']
    try:
        window.close()
        win_ui_params['exception'] = None
    except Exception as e:
        win_ui_params['exception'] = e
    return params


def winui_locate_element(params):
    win_ui_params = params['win_ui']
    parent = win_ui_params['parent']
    del win_ui_params['parent']
    if parent == 'window':
        parent_obj = win_ui_params['window']
    elif parent == 'element':
        parent_obj = win_ui_params['element']
    else:
        raise ValueError('Only window and element are allowed parent for the element!')
    try:
        if 'class_name' in win_ui_params.keys():
            class_name = win_ui_params['class_name']
            del win_ui_params['class_name']
            children = parent_obj.children(class_name=class_name)
        else:
            children = parent_obj.children()
        if 'name' in win_ui_params.keys():
            name = win_ui_params['name']
            del win_ui_params['name']
            children = [item for item in children if item.element_info.name == name]
        element = children[0]
        win_ui_params['element'] = element
        win_ui_params['exception'] = None
    except Exception as e:
        win_ui_params['exception'] = e
    return params


def winui_click_element(params):
    win_ui_params = params['win_ui']
    element = win_ui_params['element']
    click_type = win_ui_params['click_type']
    del win_ui_params['click_type']
    if 'offset' in win_ui_params.keys():
        offset = win_ui_params['offset']
        del win_ui_params['offset']
    else:
        offset = None
    try:
        lock_mouse(tgt=element, offset=offset)
        if click_type == 'left':
            element.click_input()
        elif click_type == 'right':
            element.right_click_input()
        else:
            raise NotImplementedError
        release_mouse()
        win_ui_params['exception'] = None
    except Exception as e:
        win_ui_params['exception'] = e
    return params


def winui_hint(params):
    win_ui_params = params['win_ui']
    title = win_ui_params['title']
    del win_ui_params['title']
    message = win_ui_params['message']
    del win_ui_params['message']
    messagebox.showinfo(title=title, message=message)
    return params
