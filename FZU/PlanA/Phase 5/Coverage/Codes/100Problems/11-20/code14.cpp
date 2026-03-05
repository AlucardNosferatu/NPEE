#include <iostream>
#include <vector>
#include <cassert>
using namespace std;

int main14() {
    long long n, i;
    printf("\nplease input a number:\n");
    scanf_s("%lld", &n);
    printf("%lld=", n);
    while (n % 2 == 0) {
        printf("2*");
        n = n / 2;
    }

    for (i = 3; i <= ceil(sqrt(n)); i = i + 2) {
        while (n != i)
        {
            if (n % i == 0)
            {
                printf("%lld*", i);
                n = n / i;
            }
            else
                break;
        }
    }

    printf("%lld", n);
    return 0;
}