#include <iostream>

int main09()
{
    int i, j;
    for (i = 0; i < 8; i++)
    {
        for (j = 0; j < 8; j++)
            if ((i + j) % 2 == 0)
                printf("%c%c", 161, 246);
            else
                printf("  ");
        printf("\n");
    }

    return 0;
}