#include <iostream>
#include <vector>
#include <cassert>
#include <map>
using namespace std;

int age(int n)
{
    int c;
    if (n == 1) c = 10;
    else c = age(n - 1) + 2;
    return c;
}

int main28() {
    printf("%d", age(5));
    return 0;
}