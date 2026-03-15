from my_dbg_def import *
from my_dbg_def import HMODULE, DWORD, c_char_p, c_void_p

k32 = windll.kernel32
# 设置 LoadLibraryA
k32.LoadLibraryA.argtypes = [c_char_p]
k32.LoadLibraryA.restype = HMODULE  # HMODULE 在 my_dbg_def 中定义为 c_void_p
k32.GetModuleHandleA.restype = HMODULE
k32.CloseHandle.argtypes = [HMODULE]
# 设置 GetProcAddress
k32.GetProcAddress.argtypes = [HMODULE, c_char_p]
k32.GetProcAddress.restype = c_void_p

# 设置 GetModuleFileNameA
k32.GetModuleFileNameA.argtypes = [HMODULE, c_char_p, DWORD]
k32.GetModuleFileNameA.restype = DWORD

# 设置 FreeLibrary（你后面会用到）
k32.FreeLibrary.argtypes = [HMODULE]
k32.FreeLibrary.restype = c_bool  # 如果没定义 BOOL，可以用 c_bool

# 设置 ReadProcessMemory
k32.ReadProcessMemory.argtypes = [
    HANDLE,  # hProcess
    c_void_p,  # lpBaseAddress
    c_void_p,  # lpBuffer
    c_size_t,  # nSize
    POINTER(c_size_t)  # lpNumberOfBytesRead
]
k32.ReadProcessMemory.restype = c_bool

# 设置 WriteProcessMemory
k32.WriteProcessMemory.argtypes = [
    HANDLE,  # hProcess
    c_void_p,  # lpBaseAddress
    c_void_p,  # lpBuffer (const void*)
    c_size_t,  # nSize
    POINTER(c_size_t)  # lpNumberOfBytesWritten
]
k32.WriteProcessMemory.restype = c_bool


class Debugger:
    def __init__(self):
        self.h_process = None
        self.pid = None
        self.dbg_active = False
        self.h_thread = None
        self.context = None
        self.exception_code = None
        self.exception_addr = None
        self.breakpoints = {}

    def read_process_mem(self, addr, length):
        data = b""
        read_buf = create_string_buffer(length)
        count = c_ulonglong(0)
        if not k32.ReadProcessMemory(self.h_process, addr, read_buf, length, byref(count)):
            return None
        else:
            data += read_buf.raw
            return data

    def write_process_mem(self, addr, data):
        count = c_ulonglong(0)
        length = len(data)
        c_data = c_char_p(data)
        if not k32.WriteProcessMemory(self.h_process, addr, c_data, length, byref(count)):
            return False
        else:
            return True

    def bp_set(self, addr):
        if addr not in self.breakpoints.keys():
            try:
                original_byte = self.read_process_mem(addr, 1)
                print('original_byte', original_byte)
                if not self.write_process_mem(addr=addr, data=b"\xCC"):
                    print('Cannot write process memory, err code:', k32.GetLastError())
                    return False
                else:
                    test_byte = self.read_process_mem(addr, 1)
                    print('test_byte', test_byte)
                    self.breakpoints[addr] = (addr, original_byte)
                    return True
            except Exception as e:
                print(repr(e))
                return False

    @staticmethod
    def resolve_dll_func(dll_name, func_name):
        handle = k32.GetModuleHandleA(dll_name.encode('utf-8'))
        addr = k32.GetProcAddress(handle, func_name.encode('utf-8'))
        k32.CloseHandle(handle)
        print(func_name, '的地址是', hex(addr))
        return addr

    @staticmethod
    def load(path_to_exe):
        creation_flags = DBG_PROCESS
        startup_info = STARTUP_INFO()
        process_info = PROCESS_INFORMATION()
        startup_info.dwFlags = 0x1
        startup_info.wShowWindow = 0x1

        startup_info.cb = sizeof(startup_info)
        if k32.CreateProcessA(
                path_to_exe,
                None,
                None,
                None,
                False,
                creation_flags,
                None,
                None,
                byref(startup_info),
                byref(process_info)
        ):
            print('Launched')
            print('PID:', process_info.dwProcessId)

        else:
            print('ERR:', k32.GetLastError())

    @staticmethod
    def open_process(pid):
        h_process = k32.OpenProcess(
            PROCESS_ALL_ACCESS,
            False,
            pid
        )
        return h_process

    def attach(self, pid):
        self.h_process = self.open_process(pid)
        if k32.DebugActiveProcess(pid):
            self.dbg_active = True
            self.pid = int(pid)
        else:
            print('Attach failed.')

    def run(self):
        while self.dbg_active:
            self.get_debug_event()
            cmd = input('input quit to stop.')
            if cmd.lower() in ['quit']:
                self.dbg_active = False

    def get_debug_event(self):
        debug_event = DEBUG_EVENT()
        continue_status = DBG_CONTINUE
        if k32.WaitForDebugEvent(byref(debug_event), INFINITE):
            if self.h_thread is not None:
                k32.CloseHandle(self.h_thread)
            self.h_thread = self.open_thread(tid=debug_event.dwThreadId)
            self.context = self.get_thread_ctx(h_thread=self.h_thread)
            print(
                'Event Code:', debug_event.dwDebugEventCode,
                'Thread ID:', debug_event.dwThreadId
            )
            if debug_event.dwDebugEventCode == EXCEPTION_DEBUG_EVENT:
                self.exception_code = debug_event.u.Exception.ExceptionRecord.ExceptionCode
                self.exception_addr = debug_event.u.Exception.ExceptionRecord.ExceptionAddress
            if self.exception_code == EXCEPTION_ACCESS_VIOLATION:
                print('检测到非法的内存访问')
            elif self.exception_code == EXCEPTION_BREAKPOINT:
                continue_status = self.exception_handler_breakpoint()
            elif self.exception_code == EXCEPTION_GUARD_PAGE:
                print('检测到对受保护页面的访问')
            elif self.exception_code == EXCEPTION_SINGLE_STEP:
                print('单步执行')
            else:
                if self.exception_code is not None:
                    print('非预期的异常，代码:', self.exception_code)
            k32.ContinueDebugEvent(
                debug_event.dwProcessId,
                debug_event.dwThreadId,
                continue_status
            )

    def exception_handler_breakpoint(self):
        print('断点地址:', hex(self.exception_addr))
        if self.exception_addr in self.breakpoints.keys():
            print('这是用户断点，执行恢复和回退')
            self.write_process_mem(self.exception_addr, self.breakpoints[self.exception_addr][1])
            # obtain a fresh context record, reset EIP back to the
            # original byte and then set the thread's context record
            # with the new EIP value
            self.context.Rip = self.exception_addr
            k32.SetThreadContext(self.h_thread, byref(self.context))
        return DBG_CONTINUE

    def detach(self):
        if k32.DebugActiveProcessStop(self.pid):
            print('Finished')
            return True
        else:
            print('Wrong')
            return False

    @staticmethod
    def open_thread(tid):
        h_thread = k32.OpenThread(THREAD_ALL_ACCESS, None, tid)
        if h_thread is None:
            print('Fail to obtain thread:', tid)
        return h_thread

    def enum_threads(self):
        thread_entry = THREADENTRY32()
        threads_list = []
        snapshot = k32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, self.pid)
        if snapshot is not None:
            thread_entry.dwSize = sizeof(thread_entry)
            success = k32.Thread32First(snapshot, byref(thread_entry))
            while success:
                if thread_entry.th32OwnerProcessID == self.pid:
                    threads_list.append(thread_entry.th32ThreadID)
                success = k32.Thread32Next(snapshot, byref(thread_entry))
            k32.CloseHandle(snapshot)
            return threads_list
        else:
            print('snapshot is None')
            return None

    def get_thread_ctx(self, tid=None, h_thread=None):
        ctx = CONTEXT()
        ctx.ContextFlags = CONTEXT_FULL | CONTEXT_DEBUG_REGISTERS
        if h_thread is None:
            h_thread = self.open_thread(tid=tid)
        if k32.GetThreadContext(h_thread, byref(ctx)):
            return ctx
        else:
            print('Fail to get thread contex')
            return None
