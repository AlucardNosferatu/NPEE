[org 0x7C00]
bits 16

; MBR核心：循环读取硬盘扇区到内存0x8000:0x0000
start:
    cli            ; 禁用中断
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00 ; 栈指针
    sti            ; 启用中断

    ; 🌟 清屏
    mov ah, 0x06
    mov al, 0x00
    mov bh, 0x07
    mov ch, 0x00
    mov cl, 0x00
    mov dh, 0x18
    mov dl, 0x4F
    int 0x10

    ; 设置目标地址
    mov ax, 0x8000
    mov es, ax
    xor bx, bx     ; ES:BX = 0x8000:0x0000

    ; 初始化读取参数
    mov si, 2     ; 当前扇区号（从第2扇区开始）
    mov di, 0x1A6 ; 总扇区数 = (0x354AF-0x200)/512 ≈ 422

    ; 循环读取扇区
read_loop:
    cmp di, 0
    jle read_complete ; 所有扇区读取完成

    ; 计算本次读取的扇区数（最大63）
    mov cx, di
    cmp cx, 63
    jbe .set_sectors
    mov cx, 63

.set_sectors:
    ; 保存扇区数和当前扇区号
    push cx
    push si

    ; 将LBA转换为CHS
    ; 假设：每磁道63扇区，16磁头
    mov ax, si ; LBA扇区号
    xor dx, dx
    mov bx, 63 ; 每磁道扇区数
    div bx     ; AX = 柱面，DX = 扇区-1
    
    ; 计算扇区号 (1-based)
    inc dx     ; 扇区号从1开始
    mov cl, dl ; CL低6位 = 扇区号
    
    ; 计算磁头号
    mov ax, si ; 重新加载LBA
    xor dx, dx
    mov bx, 63
    div bx     ; AX = 临时值
    xor dx, dx
    mov bx, 16 ; 磁头数
    div bx     ; DX = 磁头号
    mov dh, dl ; DH = 磁头号
    
    ; 计算柱面号
    mov ax, si   ; 重新加载LBA
    xor dx, dx
    mov bx, 1008 ; 63*16 = 每个柱面的扇区数
    div bx       ; AX = 柱面号
    mov ch, al   ; CH = 柱面号低8位
    shr ax, 2    ; 获取柱面号高2位
    and al, 0xC0 ; 只保留高2位
    or  cl, al   ; CL高2位 = 柱面号高2位

    ; 设置读取参数
    mov ah, 0x02      ; 读扇区功能
    mov al, [ss:sp+2] ; 从栈中获取扇区数
    mov dl, 0x80      ; 第一块硬盘

    ; 🔴 断点
    xchg bx, bx

    ; 调用BIOS中断读取扇区
    int 0x13
    jc  disk_error

    ; 恢复扇区号和读取的扇区数
    pop si
    pop cx

    ; 更新扇区号
    add si, cx

    ; 更新内存地址
    mov ax, cx
    shl ax, 9      ; 每个扇区512字节
    add bx, ax     ; 更新偏移
    jnc .no_carry
    ; 处理进位到段
    mov ax, es
    add ax, 0x1000
    mov es, ax

.no_carry:
    ; 更新剩余扇区数
    sub di, cx
    jmp read_loop

read_complete:
    ; 🔴 断点
    xchg bx, bx

    ; 跳转到GRUB
    jmp 0x8000:0x0000

disk_error:
    ; 错误处理
    mov  si, error_msg
    call print_string
    hlt
    jmp  $

print_string:
    pusha
    mov ah, 0x0E
    mov bh, 0x00
.print_char:
    lodsb
    test al, al
    jz   .done
    int  0x10
    jmp  .print_char
.done:
    popa
    ret

error_msg        db "Disk read error!", 0

; 填充MBR签名
times 510-($-$$) db 0
dw                  0xAA55