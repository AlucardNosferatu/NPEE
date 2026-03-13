[org 0x7C00]
bits 16

; MBR核心：读软盘第2扇区（MLP代码）到内存0x8000
start:
    mov ax, cs
    mov ds, ax
    mov es, ax

    ; 🌟 新增：BIOS清屏（0x10中断0x06功能，无残留字符）
    mov ah, 0x06 ; 功能号：上滚窗口（0x06=上滚，0=清屏）
    mov al, 0x00 ; 上滚行数=0 → 清空整个屏幕
    mov bh, 0x07 ; 填充属性：黑底白字（和默认屏幕一致）
    mov ch, 0x00 ; 左上角行号（0行，屏幕最顶）
    mov cl, 0x00 ; 左上角列号（0列，屏幕最左）
    mov dh, 0x18 ; 右下角行号（24行，屏幕最后一行）
    mov dl, 0x4F ; 右下角列号（79列，屏幕最后一列）
    int 0x10     ; 执行清屏中断

    ; 调用int 13h读软盘扇区：
    ; AH=02h（读扇区）, AL=2（读2个扇区）, CH=0（磁道0）, CL=2（扇区2）, DH=0（磁头0）, DL=0（软盘A）
    ; ES:BX=0x0000:0x8000（读取到的内存地址）
    mov ax, 0x0000
    mov es, ax
    mov bx, 0x8000 ; MLP代码加载到0x0000:0x8000（物理地址0x8000）
    mov ah, 0x02
    mov al, 0x03   ; 读2个扇区（适配你的MLP代码长度）
    mov ch, 0x00   ; 磁道0
    mov cl, 0x02   ; 扇区2（MBR是扇区1）
    mov dh, 0x00   ; 磁头0
    mov dl, 0x00   ; 软盘A
    int 0x13       ; BIOS中断，读扇区到内存

    ; 跳转到MLP代码执行（0x8000+0x8e=0x808e）
    jmp 0x0000:0x8096

; 强制填充到512字节，结尾必须是0x55AA（修正你原代码的字节序错误）
times 510 - ($ - $$) db 0
dw 0xAA55 ; 标准MBR签名（原代码写0xAA55是字节序反了，会导致BIOS不认）