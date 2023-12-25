import psutil
import win32api
import win32con
import win32process


def using_psutil(pid):
    a = psutil.Process(pid)
    print(a.name())
    print(a.username())
    print(a.cpu_times())
    a.terminate()
    print('Done')


def using_win32api(pid):
    h_process = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    info_dict = win32process.GetProcessMemoryInfo(h_process)
    win32api.TerminateProcess(h_process, 20291224)
    print(info_dict)


def get_target_pid():
    with open('pid') as f:
        lines = f.readlines()
        pid = int(lines[0])
    return pid


if __name__ is '__main__':
    p = get_target_pid()
    using_win32api(p)
