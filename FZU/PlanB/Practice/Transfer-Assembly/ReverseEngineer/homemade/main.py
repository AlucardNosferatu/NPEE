import my_dbg

if __name__ == '__main__':
    debugger = my_dbg.Debugger()
    # debugger.load(
    #     r'target.exe'.encode('utf-8')
    # )
    pid = input('Copy and Paste PID\n')
    debugger.attach(int(pid))
    # func_addr = debugger.resolve_dll_func("msvcrt.dll", "printf")
    addr = input('Copy and Paste addr\n')
    debugger.bp_set(int(addr, 16))
    debugger.run()
    debugger.detach()
