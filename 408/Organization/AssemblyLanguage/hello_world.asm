;64位没有 .model 宏指令，不能指定内存模型和调用约定
;.model flat

.data
text    db 'Hello World', 0
caption db 'Selph First x64 Application', 0
extrn   MessageBoxA: proc

.code
WinMain proc
mov     eax, 213
add     eax, 432
ret
; sub     rsp, 28h          ; 函数调用前需要预留影子空间，对齐rsp
; xor     r9d, r9d
; lea     r8,  caption
; lea     rdx, text
; xor     rcx, rcx
; call    MessageBoxA       ; 函数调用使用fastcall
; add     rsp, 28h
WinMain ENDP
END                       ; 最后直接end，不用指明符号
