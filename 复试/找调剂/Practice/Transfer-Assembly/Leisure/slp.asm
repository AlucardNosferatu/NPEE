[org 0x8000]  ; 加载到0x8000执行
bits 16

; ========== 完整MLP逻辑（浮点计算+浮点转字符串+VGA打印） ==========
; 数据区（想加多少加多少）
x1         dd 2.0
x2         dd 3.0
w11        dd 1.5
w21        dd 0.5
w12        dd 2.5
w22        dd 1.0
zero       dd 0.0
temp       dd 0.0
int_part   dd 0
fract_part dd 0
str_buf times 10 db 0
vga_seg dw 0xB800
L11     dd 0.0
L12     dd 0.0
str_L11 db 'L11=', 0
str_L12 db 'L12=', 0
ten     dd 10.0

start:
    mov  ax, cs
    mov  ds, ax
    mov  es, ax
    fninit
    ; 计算MLP第一层L11/L12
    FLD  [x1]
    FMUL [w11]
    FST  [temp]
    FSTP ST0
    FLD  [x2]
    FMUL [w21]
    FADD [temp]
    CALL relu
    FSTP [L11]

    FLD  [x1]
    FMUL [w12]
    FST  [temp]
    FSTP ST0
    FLD  [x2]
    FMUL [w22]
    FADD [temp]
    CALL relu
    FSTP [L12]

    ; 浮点转字符串+VGA打印L11
    FLD  [L11]
    CALL float_to_str
    mov  si, str_L11
    mov  di, 0x0000
    CALL print_str_to_vga
    mov  si, str_buf
    mov  di, 0x000A
    CALL print_str_to_vga

    ; 浮点转字符串+VGA打印L12
    FLD  [L12]
    CALL float_to_str
    mov  si, str_L12
    mov  di, 0x0020
    CALL print_str_to_vga
    mov  si, str_buf
    mov  di, 0x002A
    CALL print_str_to_vga

    jmp $ ; 死循环

; ========== 所有子函数（relu+浮点转字符串+VGA打印） ==========
relu:
    FCOM  [zero]
    FSTSW ax
    SAHF
    JNB   relu_end
    FLD   [zero]
relu_end:
    RET

float_to_str:
    FST  [temp]
    FSTP ST0

    ; 提取整数部分
    FLD  [temp]
    FRNDINT
    FIST [int_part]
    FSTP ST0

    ; 提取小数部分（保留1位）
    FLD   [temp]
    FLD   [temp]
    FRNDINT
    FSUBP ST1, ST0
    FMUL  [ten]
    FRNDINT
    FIST  [fract_part]
    FSTP  ST0

    ; 整数转ASCII
    mov  ax, [int_part]
    mov  di, str_buf
    CALL int_to_ascii

    ; 加小数点
    mov al, '.'
    stosb

    ; 小数转ASCII
    mov  ax, [fract_part]
    CALL int_to_ascii

    ; 结尾0
    mov al, 0
    stosb
    RET

int_to_ascii:
    push bx
    push cx
    push dx
    mov  cx, 0
    mov  bx, 10
.loop:
    xor  dx, dx
    div  bx
    push dx
    inc  cx
    cmp  ax, 0
    jne  .loop
.write:
    pop  dx
    add  dl,   '0'
    mov  [di], dl
    inc  di
    loop .write
    pop  dx
    pop  cx
    pop  bx
    RET

print_str_to_vga:
    push ax
    push bx
    push si
    push di
    push es
    mov  ax, [vga_seg]
    mov  es, ax
.print_char:
    lodsb
    cmp al,      0
    je  .print_end
    mov ah,      0x07
    mov [es:di], ax
    add di,      2
    jmp .print_char
.print_end:
    pop es
    pop di
    pop si
    pop bx
    pop ax
    RET