#include <iostream>

int main()
{
    int i, j;
    printf("%c%c\n", 161, 238); /*输出两个笑脸*/
    for (i = 1; i < 11; i++)
    {
        for (j = 1; j <= i; j++)
            printf("%c%c", 161, 246);
        printf("\n");
    }

    return 0;
}