from ctypes import *

BYTE = c_ubyte
WORD = c_ushort
DWORD = c_ulong
QWORD = c_ulonglong
LPBYTE = POINTER(c_ubyte)
LPTSTR = POINTER(c_char)
HANDLE = c_void_p
PVOID = c_void_p
HMODULE = c_void_p
UINT_PTR = c_ulonglong  # 64位下用 c_ulonglong

INFINITE = 0xFFFFFFFF
DBG_PROCESS = 0x00000001
DBG_CONTINUE = 0x00010002
CREATE_CONSOLE = 0x00000010
PROCESS_ALL_ACCESS = 0x001F0FFF
THREAD_ALL_ACCESS = 0x001F03FF

# Toolhelp32Snapshot 标志
TH32CS_SNAPHEAPLIST = 0x00000001
TH32CS_SNAPPROCESS = 0x00000002
TH32CS_SNAPTHREAD = 0x00000004
TH32CS_SNAPMODULE = 0x00000008
TH32CS_SNAPMODULE32 = 0x00000010
TH32CS_INHERIT = 0x80000000
TH32CS_SNAPALL = (TH32CS_SNAPHEAPLIST | TH32CS_SNAPPROCESS | TH32CS_SNAPTHREAD | TH32CS_SNAPMODULE)


class MODULEENTRY32(Structure):
    _fields_ = [
        ("dwSize", DWORD),
        ("th32ModuleID", DWORD),
        ("th32ProcessID", DWORD),
        ("GlblcntUsage", DWORD),
        ("ProccntUsage", DWORD),
        ("modBaseAddr", POINTER(c_byte)),  # 用 POINTER(c_byte) 更安全，后面转 int
        ("modBaseSize", DWORD),
        ("hModule", HANDLE),
        ("szModule", c_char * 260),  # ANSI 版，够用
        ("szExePath", c_char * 260),
    ]


# Context flags
CONTEXT_i386 = 0x00010000
CONTEXT_i486 = 0x00010000
CONTEXT_CONTROL = (CONTEXT_i386 | 0x00000001)
CONTEXT_INTEGER = (CONTEXT_i386 | 0x00000002)
CONTEXT_SEGMENTS = (CONTEXT_i386 | 0x00000004)
CONTEXT_FLOATING_POINT = (CONTEXT_i386 | 0x00000008)
CONTEXT_DEBUG_REGISTERS = (CONTEXT_i386 | 0x00000010)
CONTEXT_EXTENDED_REGISTERS = (CONTEXT_i386 | 0x00000020)

CONTEXT_FULL = (
        CONTEXT_CONTROL | CONTEXT_INTEGER | CONTEXT_SEGMENTS | CONTEXT_FLOATING_POINT | CONTEXT_DEBUG_REGISTERS | CONTEXT_EXTENDED_REGISTERS)

# 调试事件代码（常用）
EXCEPTION_DEBUG_EVENT = 1
CREATE_THREAD_DEBUG_EVENT = 2
CREATE_PROCESS_DEBUG_EVENT = 3
EXIT_THREAD_DEBUG_EVENT = 4
EXIT_PROCESS_DEBUG_EVENT = 5
LOAD_DLL_DEBUG_EVENT = 6
UNLOAD_DLL_DEBUG_EVENT = 7
OUTPUT_DEBUG_STRING_EVENT = 8
RIP_EVENT = 9

# 异常代码（常用）
EXCEPTION_ACCESS_VIOLATION = 0xC0000005
EXCEPTION_BREAKPOINT = 0x80000003
EXCEPTION_SINGLE_STEP = 0x80000004
EXCEPTION_GUARD_PAGE = 0x80000001


class STARTUP_INFO(Structure):
    _fields_ = [
        ("cb", DWORD),
        ("lpReserved", LPTSTR),
        ("lpDesktop", LPTSTR),
        ("lpTitle", LPTSTR),
        ("dwX", DWORD),
        ("dwY", DWORD),
        ("dwXSize", DWORD),
        ("dwYSize", DWORD),
        ("dwXCountChars", DWORD),
        ("dwYCountChars", DWORD),
        ("dwFillAttribute", DWORD),
        ("dwFlags", DWORD),
        ("wShowWindow", WORD),
        ("cbReserved2", WORD),
        ("lpReserved2", LPBYTE),
        ("hStdInput", HANDLE),
        ("hStdOutput", HANDLE),
        ("hStdError", HANDLE)
    ]


class PROCESS_INFORMATION(Structure):  # 注意：标准名字是 PROCESS_INFORMATION，不是 PROCESS_INFO
    _fields_ = [
        ("hProcess", HANDLE),
        ("hThread", HANDLE),
        ("dwProcessId", DWORD),
        ("dwThreadId", DWORD)
    ]


class EXCEPTION_RECORD(Structure):
    pass


EXCEPTION_RECORD._fields_ = [
    ("ExceptionCode", DWORD),
    ("ExceptionFlags", DWORD),
    ("ExceptionRecord", POINTER(EXCEPTION_RECORD)),
    ("ExceptionAddress", PVOID),
    ("NumberParameters", DWORD),
    ("ExceptionInformation", UINT_PTR * 15),
]


class EXCEPTION_DEBUG_INFO(Structure):
    _fields_ = [
        ("ExceptionRecord", EXCEPTION_RECORD),
        ("dwFirstChance", DWORD),
    ]


class CREATE_THREAD_DEBUG_INFO(Structure):
    _fields_ = [
        ("hThread", HANDLE),
        ("lpThreadLocalBase", PVOID),
        ("lpStartAddress", PVOID),
    ]


class DEBUG_EVENT_UNION(Union):
    _fields_ = [
        ("Exception", EXCEPTION_DEBUG_INFO),
        ("CreateThread", CREATE_THREAD_DEBUG_INFO),
        # 可以继续补其他：CREATE_PROCESS_DEBUG_INFO, EXIT_THREAD_DEBUG_INFO 等
        # 如果需要再加，告诉我，我帮你补
    ]


class DEBUG_EVENT(Structure):
    _fields_ = [
        ("dwDebugEventCode", DWORD),
        ("dwProcessId", DWORD),
        ("dwThreadId", DWORD),
        ("u", DEBUG_EVENT_UNION),
    ]


class THREADENTRY32(Structure):
    _fields_ = [
        ("dwSize", DWORD),
        ("cntUsage", DWORD),
        ("th32ThreadID", DWORD),
        ("th32OwnerProcessID", DWORD),
        ("tpBasePri", DWORD),
        ("tpDeltaPri", DWORD),
        ("dwFlags", DWORD),
    ]


# ────────────────────────────────────────────────
#               64位 CONTEXT 定义（AMD64）
# ────────────────────────────────────────────────

class M128A(Structure):
    _fields_ = [
        ("Low", c_ulonglong),
        ("High", c_ulonglong),
    ]


class XMM_SAVE_AREA32(Structure):
    _fields_ = [
        ("ControlWord", c_ushort),
        ("StatusWord", c_ushort),
        ("TagWord", c_ubyte),
        ("Reserved1", c_ubyte),
        ("ErrorOpcode", c_ushort),
        ("ErrorOffset", c_ulong),
        ("ErrorSelector", c_ushort),
        ("Reserved2", c_ushort),
        ("DataOffset", c_ulong),
        ("DataSelector", c_ushort),
        ("Reserved3", c_ushort),
        ("MxCsr", c_ulong),
        ("MxCsr_Mask", c_ulong),
        ("FloatRegisters", M128A * 8),
        ("XmmRegisters", M128A * 16),
        ("Reserved4", c_ubyte * 96),
    ]


class CONTEXT(Structure):
    _pack_ = 16  # 必须 16 字节对齐
    _fields_ = [
        ("P1Home", c_ulonglong),
        ("P2Home", c_ulonglong),
        ("P3Home", c_ulonglong),
        ("P4Home", c_ulonglong),
        ("P5Home", c_ulonglong),
        ("P6Home", c_ulonglong),

        ("ContextFlags", c_ulong),
        ("MxCsr", c_ulong),

        ("SegCs", c_ushort),
        ("SegDs", c_ushort),
        ("SegEs", c_ushort),
        ("SegFs", c_ushort),
        ("SegGs", c_ushort),
        ("SegSs", c_ushort),
        ("EFlags", c_ulong),

        ("Dr0", c_ulonglong),
        ("Dr1", c_ulonglong),
        ("Dr2", c_ulonglong),
        ("Dr3", c_ulonglong),
        ("Dr6", c_ulonglong),
        ("Dr7", c_ulonglong),

        ("Rax", c_ulonglong),
        ("Rcx", c_ulonglong),
        ("Rdx", c_ulonglong),
        ("Rbx", c_ulonglong),
        ("Rsp", c_ulonglong),
        ("Rbp", c_ulonglong),
        ("Rsi", c_ulonglong),
        ("Rdi", c_ulonglong),
        ("R8", c_ulonglong),
        ("R9", c_ulonglong),
        ("R10", c_ulonglong),
        ("R11", c_ulonglong),
        ("R12", c_ulonglong),
        ("R13", c_ulonglong),
        ("R14", c_ulonglong),
        ("R15", c_ulonglong),
        ("Rip", c_ulonglong),

        # 浮点 / XMM 部分（占位，够基本调试用）
        ("Legacy", M128A * 8),
        ("Xmm0", M128A),
        ("Xmm1", M128A),
        ("Xmm2", M128A),
        ("Xmm3", M128A),
        ("Xmm4", M128A),
        ("Xmm5", M128A),
        ("Xmm6", M128A),
        ("Xmm7", M128A),
        ("Xmm8", M128A),
        ("Xmm9", M128A),
        ("Xmm10", M128A),
        ("Xmm11", M128A),
        ("Xmm12", M128A),
        ("Xmm13", M128A),
        ("Xmm14", M128A),
        ("Xmm15", M128A),

        ("VectorRegister", M128A * 26),
        ("VectorControl", c_ulonglong),

        ("DebugControl", c_ulonglong),
        ("LastBranchToRip", c_ulonglong),
        ("LastBranchFromRip", c_ulonglong),
        ("LastExceptionToRip", c_ulonglong),
        ("LastExceptionFromRip", c_ulonglong),
    ]
