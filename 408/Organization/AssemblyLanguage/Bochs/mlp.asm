[org 0x8000]  ; 加载基地址固定为0x8000
bits 16

; ========== 数据区（仅修改x1/x2初始值，其余完全复用） ==========
; 【输入层】（原固定值改为初始0.0，会被键盘输入覆盖）
x1         dd 0.0       ; 输入1（键盘输入第一位：0→0.0，1→100.0）
x2         dd 0.0       ; 输入2（键盘输入第二位：0→0.0，1→100.0）

; 【第一层：输入层→隐藏层1（2→2）】（完全复用）
w11        dd 1.5       ; x1 → L11
w21        dd 0.5       ; x2 → L11
w12        dd 2.5       ; x1 → L12
w22        dd 1.0       ; x2 → L12
L11        dd 0.0       ; 隐藏层1输出1
L12        dd 0.0       ; 隐藏层1输出2
str_L11    db 'L11=', 0 ; 打印标签
str_L12    db 'L12=', 0 ; 打印标签

; 【第二层：隐藏层1→隐藏层2（2→2）】（完全复用）
w11_2      dd 2.0       ; L11 → L21
w21_2      dd 1.0       ; L12 → L21
w12_2      dd 0.5       ; L11 → L22
w22_2      dd 3.0       ; L12 → L22
L21        dd 0.0       ; 隐藏层2输出1
L22        dd 0.0       ; 隐藏层2输出2
str_L21    db 'L21=', 0 ; 打印标签
str_L22    db 'L22=', 0 ; 打印标签

; 【第三层：隐藏层2→输出层（2→2）】（完全复用）
w11_3      dd 1.2       ; L21 → L31
w21_3      dd 0.8       ; L22 → L31
w12_3      dd 2.5       ; L21 → L32
w22_3      dd 1.8       ; L22 → L32
L31        dd 0.0       ; 最终输出1
L32        dd 0.0       ; 最终输出2
str_L31    db 'L31=', 0 ; 打印标签
str_L32    db 'L32=', 0 ; 打印标签

; 【辅助变量（完全复用）】
zero       dd 0.0       ; ReLU比较用的0.0
temp       dd 0.0       ; 临时存储中间结果
int_part   dd 0         ; 浮点转字符串-整数部分
fract_part dd 0         ; 浮点转字符串-小数部分
str_buf times 10 db 0 ; 字符串缓冲区
vga_seg   dw 0xB800 ; VGA显存段地址
ten       dd 10.0   ; 小数部分放大10倍用
; 新增：浮点常量（0.0/100.0，供输入转换用）
float_0   dd 0.0
float_100 dd 100.0

; ========== 程序入口（新增键盘输入逻辑，后接原有MLP计算） ==========
start:
    xchg   bx, bx
    mov    ax, cs
    mov    ds, ax
    mov    es, ax
    fninit        ; 初始化FPU（保留原有逻辑）

    ; ===================== 新增：键盘读取两位0/1 → 赋值x1/x2 =====================
    ; 1. 读取第一位（x1的输入：0→0.0，1→100.0）
read_bit1:
    mov ah, 00h    ; BIOS int 16h：等待读取按键（AL=ASCII码）
    int 16h
    cmp al, '0'    ; 仅接收'0'或'1'
    je  set_x1_0
    cmp al, '1'
    je  set_x1_100
    jmp read_bit1  ; 非0/1则重试

set_x1_0: ; 第一位是0 → x1=0.0
    fld  dword [float_0]
    fstp dword [x1]
    jmp  read_bit2

set_x1_100: ; 第一位是1 → x1=100.0
    fld  dword [float_100]
    fstp dword [x1]
    jmp  read_bit2

    ; 2. 读取第二位（x2的输入：0→0.0，1→100.0）
read_bit2:
    mov ah, 00h
    int 16h
    cmp al, '0'
    je  set_x2_0
    cmp al, '1'
    je  set_x2_100
    jmp read_bit2  ; 非0/1则重试

set_x2_0: ; 第二位是0 → x2=0.0
    fld  dword [float_0]
    fstp dword [x2]
    jmp  mlp_calc        ; 输入完成，跳转到MLP计算

set_x2_100: ; 第二位是1 → x2=100.0
    fld  dword [float_100]
    fstp dword [x2]

    ; ===================== 原有MLP计算逻辑（完全复用，无修改） =====================
mlp_calc:
    ; -------------------- 第一层计算：输入→L11/L12 --------------------
    ; L11 = ReLU(x1*w11 + x2*w21)
    FLD  [x1]
    FMUL [w11]
    FST  [temp]
    FSTP ST0
    FLD  [x2]
    FMUL [w21]
    FADD [temp]
    CALL relu
    FSTP [L11]

    ; L12 = ReLU(x1*w12 + x2*w22)
    FLD  [x1]
    FMUL [w12]
    FST  [temp]
    FSTP ST0
    FLD  [x2]
    FMUL [w22]
    FADD [temp]
    CALL relu
    FSTP [L12]

    ; -------------------- 第二层计算：L11/L12→L21/L22 --------------------
    ; L21 = ReLU(L11*w11_2 + L12*w21_2)
    FLD  [L11]
    FMUL [w11_2]
    FST  [temp]
    FSTP ST0
    FLD  [L12]
    FMUL [w21_2]
    FADD [temp]
    CALL relu
    FSTP [L21]

    ; L22 = ReLU(L11*w12_2 + L12*w22_2)
    FLD  [L11]
    FMUL [w12_2]
    FST  [temp]
    FSTP ST0
    FLD  [L12]
    FMUL [w22_2]
    FADD [temp]
    CALL relu
    FSTP [L22]

    ; -------------------- 第三层计算：L21/L22→L31/L32 --------------------
    ; L31 = ReLU(L21*w11_3 + L22*w21_3)
    FLD  [L21]
    FMUL [w11_3]
    FST  [temp]
    FSTP ST0
    FLD  [L22]
    FMUL [w21_3]
    FADD [temp]
    CALL relu
    FSTP [L31]

    ; L32 = ReLU(L21*w12_3 + L22*w22_3)
    FLD  [L21]
    FMUL [w12_3]
    FST  [temp]
    FSTP ST0
    FLD  [L22]
    FMUL [w22_3]
    FADD [temp]
    CALL relu
    FSTP [L32]

    ; ===================== VGA打印逻辑（完全复用） =====================
    ; ------------- 第一层：第一行（VGA行0，起始偏移0x0000） -------------
    FLD  [L11]
    CALL float_to_str
    mov  si, str_L11
    mov  di, 0x0000
    CALL print_str_to_vga
    mov  si, str_buf
    mov  di, 0x0008
    CALL print_str_to_vga

    FLD  [L12]
    CALL float_to_str
    mov  si, str_L12
    mov  di, 0x0020
    CALL print_str_to_vga
    mov  si, str_buf
    mov  di, 0x0028
    CALL print_str_to_vga

    ; ------------- 第二层：第二行（VGA行1，起始偏移0x00A0） -------------
    FLD  [L21]
    CALL float_to_str
    mov  si, str_L21
    mov  di, 0x00A0
    CALL print_str_to_vga
    mov  si, str_buf
    mov  di, 0x00A8
    CALL print_str_to_vga

    FLD  [L22]
    CALL float_to_str
    mov  si, str_L22
    mov  di, 0x00C0
    CALL print_str_to_vga
    mov  si, str_buf
    mov  di, 0x00C8
    CALL print_str_to_vga

    ; ------------- 第三层：第三行（VGA行2，起始偏移0x0140） -------------
    FLD  [L31]
    CALL float_to_str
    mov  si, str_L31
    mov  di, 0x0140
    CALL print_str_to_vga
    mov  si, str_buf
    mov  di, 0x0148
    CALL print_str_to_vga

    FLD  [L32]
    CALL float_to_str
    mov  si, str_L32
    mov  di, 0x0160
    CALL print_str_to_vga
    mov  si, str_buf
    mov  di, 0x0168
    CALL print_str_to_vga

    jmp start+2 ; 死循环（防止程序跑飞）

; ========== 原有子函数（完全复用，无任何修改） ==========
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

    ; 字符串结尾置0
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
    mov ah,      0x07 ; 字符属性：黑底白字（可改0x0F白字黑底）
    mov [es:di], ax
    add di,      2    ; VGA显存每个字符占2字节（ASCII+属性）
    jmp .print_char
.print_end:
    pop es
    pop di
    pop si
    pop bx
    pop ax
    RET