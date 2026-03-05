#include <iostream>
#include <vector>
#include <cassert>
#include <set>
#include <map>
using namespace std;

int main24() {
    int n, t, number = 20;
    float a = 2, b = 1, s = 0;
    for (n = 1; n <= number; n++)
    {
        s = s + a / b;
        t = a; a = a + b; b = t;/*这部分是程序的关键，请读者猜猜t的作用*/
    }
    printf("sum is %9.6f\n", s);
    return 0;
}