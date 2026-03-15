#include <windows.h>
#include <stdio.h>
#pragma comment(lib, "user32.lib")

__declspec(noinline) void test_func()
{
    printf("Target activated, PID = %u\n", GetCurrentProcessId());
    printf("test_func address (inside): %p\n", test_func);
}

int main()
{
    printf("Press ESC to exit.\n");
    while (1)
    {
        test_func(); // 调用测试函数
        Sleep(1000);
        if (GetAsyncKeyState(VK_ESCAPE) & 0x8000)
            break;
    }
    return 0;
}