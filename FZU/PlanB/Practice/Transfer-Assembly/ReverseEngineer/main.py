import py3dbg
from py3dbg import *

PROCESS_NAME = r'C:\Users\16413\Desktop\NPEE\NPEE\FZU\PlanB\Practice\Transfer-Assembly\ReverseEngineer\target\target.exe'.encode(
    'utf-8')


def callback(dbg: pydbg):
    _ = dbg
    print('hit printf')
    return py3dbg.DBG_CONTINUE


if __name__ == "__main__":
    # addr = input('Copy and Paste addr\n')
    dbg_ = pydbg()
    dbg_.load(PROCESS_NAME)
    # dbg_.set_callback(py3dbg.defines.EXCEPTION_BREAKPOINT, callback)
    dbg_.attach(dbg_.pid)
    printf_addr = dbg_.func_resolve(dll=PROCESS_NAME, function=b'test_func')
    dbg_.bp_set(address=printf_addr, handler=callback)
    dbg_.run()
