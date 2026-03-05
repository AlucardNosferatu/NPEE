#include <iostream>
#include <vector>
#include <cassert>
using namespace std;

int main18() {
    int a, n = 1;

    printf("please input a and n\n");
    scanf_s("%d,%d", &a, &n);
    printf("a=%d,n=%d\n", a, n);
    int base_case = a * n;
    int temp=base_case;
    int sum = 0;
    for (int i = 0; i < n; i++) {
        sum = sum + temp;
        temp = (base_case - (a*(i+1))) * pow(10,i+1);
    }
    printf("%d", sum);
    return 0;
}