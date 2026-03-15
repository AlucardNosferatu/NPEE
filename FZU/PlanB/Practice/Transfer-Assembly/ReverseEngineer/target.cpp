// target.c - 简单可调试靶子
#include <windows.h>
#include <stdio.h>

int main()
{
    while (1)
    {
        printf("靶子已启动，PID = %u\n", GetCurrentProcessId());
        Sleep(1000);
    }
    return 0;
}