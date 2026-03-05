#include <iostream>
#include <vector>
#include <cassert>
#include <map>
using namespace std;

map<int, int> factorial_mem;

int factorial(int n) {
    if (factorial_mem.count(n) <= 0) {
        int res;
        if (n <= 1) {
            res = 1;
        }
        else {
            res = n * factorial(n - 1);
        }
        factorial_mem[n] = res;
    }
    return factorial_mem[n];
}

int main26() {
    int i = 5;
    printf("%d!=%d\n", i, factorial(i));
    return 0;
}