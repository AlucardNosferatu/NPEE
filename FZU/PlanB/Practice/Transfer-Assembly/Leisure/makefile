# 声明伪目标：避免当前目录有同名文件时，Make 误判为“已生成”
.PHONY: all clean_mlp clean_lk

# 默认目标：执行 make 时，先做 all（生成img），再自动做 clean（清理）
all: mbr.img mbr_lk.img clean_mlp clean_lk


mbr_lk.img: lk_mbr.bin grldr
	copy /b lk_mbr.bin + grldr mbr_lk.img
	powershell ".\hdd_img.ps1 -InputFile mbr_lk.img"

lk_mbr.bin: lk_mbr.asm
	nasm lk_mbr.asm -f bin -o lk_mbr.bin

clean_lk:
	del lk_mbr.bin

mbr.img: mlp_mbr.bin mlp.bin
	copy /b mlp_mbr.bin + mlp.bin mbr.img

mlp_mbr.bin: mlp_mbr.asm
	nasm mlp_mbr.asm -f bin -o mlp_mbr.bin

mlp.bin: mlp.asm
	nasm mlp.asm -f bin -o mlp.bin

clean_mlp:
	del mlp_mbr.bin
	del mlp.bin