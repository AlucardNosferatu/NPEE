import psutil
import win32api
import win32con


def using_psutil():
    a = psutil.Process(14792)
    print(a.name())
    print(a.username())
    print(a.cpu_times())
    a.terminate()
    print('Done')


def using_win32api(pid):
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    win32api.TerminateProcess(handle, 20291224)
    print('Done')


def get_target_pid():
    with open('pid') as f:
        lines = f.readlines()
        pid = int(lines[0])
    return pid


if __name__ is '__main__':
    p = get_target_pid()
    using_win32api(p)
