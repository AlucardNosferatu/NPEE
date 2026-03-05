#include <iostream>
#include <vector>
#include <cassert>
#include <map>
using namespace std;



int main() {
    string num;
    cin >> num;
    int length = num.size();
    int j;
    bool palin = true;
    for (int i = 0; i < length; i++) {
        j = length - i - 1;
        if (num[i] != num[j]) {
            palin = false;
            break;
        }
    }
    printf("%s", palin ? "Yes" : "No");
    return 0;
}