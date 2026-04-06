from ctypes import *

msvcrt = cdll.msvcrt

input('attached?')
buffer = c_char_p(b"AAAAA")
overflow = b"A" * 1000

msvcrt.strcpy(buffer, overflow)
print('Done')
