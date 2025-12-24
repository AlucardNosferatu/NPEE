; 文件名：pygmalion_perfect.asm
; 编译命令：nasm -f bin pygmalion_perfect.asm -o pygmalion_perfect.bin
; 核心功能：左上角固定位置 + A-Z→A无限循环 + 肉眼清晰切换
org     0x7C00 ; MBR加载地址
bits    16     ; 16位实模式

section .text
start:
    ; 初始化VGA（一次到位，全程不修改）
    mov ax, 0xB800 ; VGA段地址
    mov es, ax     ; es=0xB800
    mov ah, 0x0E   ; 黄色背景+黑色字符（醒目）

main_loop:
    mov bl, 0x41 ; 起始字符'A'（0x41）
char_loop:
    mov   di, 0x0000 ; 强制固定左上角（不跑位）
    mov   al, bl     ; al=当前字符
    stosw            ; 写字符到VGA（触发刷新）
    inc   bl         ; 字符+1（A→B→...→Z）
    
    ; 🔥 核心修复：Z（0x5A）之后重置为A（0x41），不超界
    cmp bl, 0x5B ; 判断是否超过Z（Z=0x5A，0x5B是下一个字符[）
    jne no_reset ; 没超过→继续
    mov bl, 0x41 ; 超过了→重置为A
no_reset:

    call delay_800ms ; 0.8秒切换一次
    jmp  char_loop   ; 无限循环（不用cx计数，靠判断重置实现A-Z循环）

; 0.8秒延时（切换流畅，看清变化）
delay_800ms:
    mov cx, 0x0180
outer:
    mov dx, 0xFFFF
inner:
    dec dx
    jnz inner
    dec cx
    jnz outer
    ret

; MBR强制512字节，引导正常
times 510 - ($ - $$) db 0
dw 0xAA55 ; MBR结束标志