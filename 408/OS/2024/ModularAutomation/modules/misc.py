import code
import datetime
import os
import threading
import time
from typing import Union, List

from scapy.volatile import RandMAC

from modules.encryption.eweb_password import encrypt_pass

time_format = "%Y年%m月%d日-%H时%M分%S秒"
input_handler = None


def nop(params):
    """
    什么也不做，用来分隔两个Hook
    """
    return params


def interactive_shell(params):
    global input_handler
    # noinspection PyUnresolvedReferences
    input_handler.kill()
    input_handler = None
    code.interact(local=locals(), banner='输入Ctrl+Z结束交互式控制台')
    return params


def get_input_str(params):
    global input_handler
    misc_params = params['misc']
    if 'input_prompt' in misc_params.keys():
        print(misc_params['input_prompt'])
    if input_handler is None:
        input_handler = NonBlockingStdIn()
    misc_params['input_str'] = '\n'.join(input_handler.get_all_lines_wait_empty())
    return params


def eweb_pass_enc(params):
    """
    加密EWEB密码的明文
    """
    misc_params = params['misc']
    ep_dec = misc_params['ep_dec']
    ep_enc = encrypt_pass(message=ep_dec)
    misc_params['ep_enc'] = ep_enc
    return params


def timer(params):
    """
    一次性计时器，先开后关
    """
    misc_params = params['misc']
    timer_params = misc_params['timer']
    while not timer_params['start']:
        pass
    timer_params['time_start'] = datetime.datetime.now()
    while not timer_params['stop']:
        timer_params['time_end'] = datetime.datetime.now()
        timer_params['time_delta'] = timer_params['time_end'] - timer_params['time_start']
    return params


def timer_transience(params):
    """
    打点计时器，多点记录（时间表）
    """
    misc_params = params['misc']
    timer_params = misc_params['timer']
    if 't_name' in timer_params:
        t_name = timer_params['t_name']
        # del timer_params['t_name']
        if 't_table' not in timer_params:
            timer_params['t_table'] = {}
        if t_name not in timer_params['t_table'].keys():
            timer_params['t_table'][t_name] = []
        if 't_desc' in timer_params:
            t_desc = timer_params['t_desc']
            del timer_params['t_desc']
        else:
            t_desc = ''
        t = datetime.datetime.now()
        timer_params['t_table'][t_name].append([t, t_desc])
        params['misc']['exception'] = None
    else:
        err = '缺少t_name，无法记录时刻'
        print(err)
        params['misc']['exception'] = err
    return params


def process_kill(params):
    """
    干掉进程
    """
    misc_params = params['misc']
    kill_processes = misc_params['kill_processes']
    for i in range(len(kill_processes)):
        pid = kill_processes[i]
        try:
            os.system('taskkill /f /pid {}'.format(pid))
            print('结束pids   {}'.format(str(pid)))
            kill_processes[i] = [pid, True, None]
        except BaseException as e:
            print('异常:{}'.format(repr(e)))
            kill_processes[i] = [pid, False, e]
    return params


def mac_generate(params):
    """
    生成单播MAC地址
    """
    misc_params = params['misc']
    finished = False
    new_mac = None
    while not finished:
        new_mac = str(RandMAC())
        if new_mac[1].lower() in ['1', '3', '5', '7', '9', 'b', 'd', 'f']:
            continue
        finished = True
    assert new_mac is not None
    misc_params['new_mac'] = new_mac
    return params


def mac_increase(params):
    """
    根据base_mac自增1获取新MAC地址
    """
    misc_params = params['misc']
    base_mac = misc_params['base_mac']
    # base_mac = '00:d0:f8:22:31:29'
    mac_str_hex = base_mac.replace(':', '')
    mac_dec = int(mac_str_hex, 16)
    mac_dec_new = mac_dec + 1
    new_mac = str(hex(mac_dec_new)).split('x')[1]
    while len(new_mac) < 12:
        new_mac = '0' + new_mac
    new_mac = list(new_mac)
    new_mac.insert(2, ':')
    new_mac.insert(4 + 1, ':')
    new_mac.insert(6 + 2, ':')
    new_mac.insert(8 + 3, ':')
    new_mac.insert(10 + 4, ':')
    new_mac = ''.join(new_mac)
    misc_params['new_mac'] = new_mac
    return params


def mac_read_record(params):
    """
    从txt文件或list中读取MAC地址记录
    """
    misc_params = params['misc']
    if 'mac_record_file' not in misc_params.keys():
        mac_record_file = 'reports/mac_record.txt'
    else:
        mac_record_file = misc_params['mac_record_file']
    if not os.path.exists(mac_record_file):
        with open(file=mac_record_file, mode='w') as f:
            f.writelines([])
    with open(file=mac_record_file, mode='r') as f:
        mac_record = f.readlines()
        mac_record = [mac.strip() for mac in mac_record]
    misc_params['mac_record'] = mac_record
    return params


def mac_write_record(params):
    """
    把MAC地址记录写入txt文件或list
    """
    misc_params = params['misc']
    if 'mac_record_file' not in misc_params.keys():
        mac_record_file = 'reports/mac_record.txt'
    else:
        mac_record_file = misc_params['mac_record_file']
    if not os.path.exists(mac_record_file):
        with open(file=mac_record_file, mode='w') as f:
            f.writelines([])
    if 'mac_record' not in misc_params.keys():
        mac_record = []
    else:
        mac_record = misc_params['mac_record']
    with open(file=mac_record_file, mode='w') as f:
        f.writelines('\n'.join(mac_record))
    return params


def mac_input_record(params):
    """
    手动输入MAC地址记录
    """
    params['misc'] = {}
    params['misc']['new_mac_list'] = []
    for i in range(4):
        if i == 0:
            params['misc']['new_mac'] = input(
                '输入已知MAC的起始地址（例:38:db:35:46:82:a3）').lower()
        else:
            params = mac_increase(params=params)
        params['misc']['base_mac'] = params['misc']['new_mac']
        params['misc']['new_mac_list'].append(params['misc']['new_mac'])
    params = mac_read_record(params=params)
    for mac in params['misc']['new_mac_list']:
        if mac not in params['misc']['mac_record']:
            params['misc']['mac_record'].append(mac)
    params = mac_write_record(params=params)
    [print(mac) for mac in params['misc']['new_mac_list']]
    return params


def mac_input_record_loop(params):
    """
    手动输入MAC地址记录，循环进行
    """
    while True:
        params = mac_input_record(params=params)
        cmd = input('按任意键输入下一个MAC，输入exit退出')
        if cmd == 'exit':
            break


def iface_ip(params):
    """
    查看接口的IP地址
    """
    misc_params = params['misc']
    iface_name = misc_params['iface_name']
    with os.popen('ipconfig') as fp:
        bf = fp.buffer.read()
        try:
            lines = bf.decode().strip()
        except UnicodeDecodeError:
            lines = bf.decode('gbk').strip()
    lines = lines.replace('\r', '\n')
    while '\n\n' in lines:
        lines = lines.replace('\n\n', '\n')
    lines = lines.split('\n')
    lines.pop(0)
    all_iface_dict = {}
    current_iface = ''
    for line in lines:
        if not line.startswith('   '):
            current_iface = line.strip()
            all_iface_dict[current_iface] = {}
        else:
            line_pair = line.split('. . . . . . . :')
            key1, val = line_pair[0].strip(), line_pair[1].strip()
            all_iface_dict[current_iface][key1] = val
    misc_params['iface_ip'] = None
    for key1 in all_iface_dict.keys():
        if iface_name in key1:
            for key2 in all_iface_dict[key1].keys():
                if 'IPv4 地址' in key2:
                    misc_params['iface_ip'] = all_iface_dict[key1][key2]
    return params


def ip_ping(params):
    """
    去ping一个IP地址
    """
    misc_params = params['misc']
    ping_host = misc_params['ping_host']
    ping_times = misc_params['ping_times']
    # 在Linux/Mac上使用-c参数，在Windows上使用-n参数
    response = os.system(f"ping -n {ping_times} {ping_host}")
    if response == 0:
        misc_params['ping_result'] = [True, f"{ping_host}可达"]
    else:
        misc_params['ping_result'] = [False, f"{ping_host}不可达"]
    return params


class NonBlockingStdIn:
    """NonBlockingStdIn
    Spawns a thread on creation that automatically reads and buffers stdin.
    This allows for a non-blocking line-buffered stdin.
    In the event of nothing being buffered None is returned.

    Side note: If stdin is read by anything else eternal suffering may ensue.
    Singleton facilities may be implemented soon(tm)."""

    def __init__(self, line_limit: int = 0) -> None:
        """Create a NonBlockingStdIn instance.

        Keyword arguments:
        line_limit -- max buffered lines (default 0 [infinite])"""

        # Attributes are private to prevent severe turmoil
        self.__line_limit = abs(line_limit) or float('inf')
        self.__kill_flag = threading.Event()
        self.__lines = []
        self.__lines_lock = threading.Lock()
        self.__thread = threading.Thread(target=self.__input_collector)
        self.__thread.start()

    def __input_collector(self) -> None:
        """Input thread target. Continuously collects stdin into __lines."""
        while True:
            if self.__kill_flag.is_set():
                return
            elif len(self.__lines) < self.__line_limit:
                try:
                    line = input()
                except EOFError:
                    continue
                self.__lines_lock.acquire()
                self.__lines.append(line)
                self.__lines_lock.release()

    def input(self) -> Union[str, None]:
        """Pop one line from the buffer. Returns None when the buffer is empty."""
        self.__lines_lock.acquire()
        line = None
        if len(self.__lines) > 0:
            line = self.__lines.pop(0)
        self.__lines_lock.release()
        return line

    def num_available_lines(self) -> int:
        """Return number of lines buffered."""
        self.__lines_lock.acquire()
        amount = len(self.__lines)
        self.__lines_lock.release()
        return amount

    def get_all_lines(self) -> List[str]:
        """Return all buffered lines and clear buffer."""
        self.__lines_lock.acquire()
        lines = self.__lines
        self.__lines = []
        self.__lines_lock.release()
        return lines

    def get_all_lines_wait_empty(self) -> List[str]:
        while len(self.__lines) <= 0:
            time.sleep(0.01)
        return self.get_all_lines()

    def kill(self):
        """Kill input thread to restore predictable usage of input().

        Note: Currently requires to be input to stdin to stop the thread being blocked.
        """
        self.__kill_flag.set()
        print('Please hit [ENTER]')
        self.__thread.join()


if __name__ == '__main__':
    print('Done')
