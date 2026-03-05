#include <iostream>
#include <vector>
#include <cassert>
#include <map>
using namespace std;



int main27() {
    int length = 5;
    vector<char> stack;
    char temp;
    for (int i = 0; i < length; i++) {
        scanf_s("%c", &temp, 1);
        stack.push_back(temp);
    }
    for (int i = 0; i < length; i++) {
        printf("%c", stack.back());
        stack.pop_back();
    }
    printf("\n");
    return 0;
}