#include <iostream>
#include <vector>
#include <cassert>
#include <map>
using namespace std;



int main25() {
    long long sum = 1;
    long long f = 1;
    for (int i = 2; i <= 20; i++) {
        f = f * i;
        sum = sum + f;
    }
    printf("1+2!+3!...+20!=%lld\n", sum);
    return 0;
}