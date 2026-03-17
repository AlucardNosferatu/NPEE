import py3dbg
from py3dbg import *

from utils import crash_binning

# PROCESS_NAME = r'C:\Users\16413\Desktop\NPEE\NPEE\FZU\PlanB\Practice\Transfer-Assembly\ReverseEngineer\target\target.exe'.encode(
#     'utf-8')
PROCESS_NAME = r'C:\Users\16413\AppData\Local\Programs\Python\Python310\python.exe'.encode('utf-8')
target_py = r'C:\Users\16413\Desktop\NPEE\NPEE\FZU\PlanB\Practice\Transfer-Assembly\ReverseEngineer\target\target_overflow.py'.encode(
    'utf-8')


def callback(dbg: pydbg):
    _ = dbg
    print('hit breakpoint')
    return py3dbg.DBG_CONTINUE


def callback_overflow(dbg: pydbg):
    print('hit overflow')
    crash_bin = crash_binning.crash_binning()
    crash_bin.record_crash(pydbg=dbg)
    print(crash_bin.crash_synopsis())
    return py3dbg.DBG_EXCEPTION_NOT_HANDLED


if __name__ == "__main__":
    # addr = input('Copy and Paste addr\n')
    dbg_ = pydbg()
    dbg_.load(path_to_file=PROCESS_NAME, command_line=target_py)
    dbg_.attach(dbg_.pid)
    dbg_.set_callback(py3dbg.defines.EXCEPTION_ACCESS_VIOLATION, callback_overflow)
    # printf_addr = dbg_.func_resolve(dll=PROCESS_NAME, function=b'test_func')
    # dbg_.bp_set(address=printf_addr, handler=callback)
    dbg_.run()
