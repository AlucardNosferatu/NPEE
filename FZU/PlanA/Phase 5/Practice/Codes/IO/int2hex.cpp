#include <iostream>

using namespace std;

int main()
{
    int original_dec;
    scanf("%d", &original_dec); // 读取原始十进制数
    printf("%08X", original_dec);
    return 0;
}