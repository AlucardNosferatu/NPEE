#include <iostream>

using namespace std;

int main()
{
    int dim;
    scanf("%d", &dim);
    for (int i = 0; i < dim; i++)
    {
        for (int j = 0; j < dim; j++)
        {
            printf("%4d", (i + 1) * (j + 1));
        }
        printf("\n");
    }
    return 0;
}