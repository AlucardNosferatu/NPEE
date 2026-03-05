#include <cassert>
#include <iostream>

int main05()
{
    int x, y, z;
    scanf_s("%d,%d,%d", &x, &y, &z);
    if (x < y) {
        x = x + y;
        y = x - y;
        x = x - y;
    }
    assert(x >= y);
    if (y < z) {
        y = y + z;
        z = y - z;
        y = y - z;
    }
    assert(y >= z);
    if (x < y) {
        x = x + y;
        y = x - y;
        x = x - y;
    }
    assert(x >= z);
    printf("%d,%d,%d", x, y, z);
    return 0;
}