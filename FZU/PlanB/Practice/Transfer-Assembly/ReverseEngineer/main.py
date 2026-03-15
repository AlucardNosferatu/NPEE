import my_dbg

if __name__ == '__main__':
    debugger = my_dbg.Debugger()
    # debugger.load(
    #     r'target.exe'.encode('utf-8')
    # )
    pid = input('Copy and Paste PID\n')
    debugger.attach(int(pid))
    local_func, local_base, rva = debugger.resolve_dll_func("msvcrt.dll", "printf19124")
    debugger.bp_set(local_func)
    # debugger.run()
    debugger.detach()
