#include <iostream>
#include <vector>
#include <cassert>
#include <set>
#include <map>
using namespace std;

int main22() {
    map<int, char> names = { {0,'x'},{1,'y'},{2,'z'} };
    set<int> dm_a = { 0 };
    set<int> dm_c = { 0,2 };
    int a_oppo;
    int b_oppo;
    int c_oppo;
    bool found = false;
    for (int i = 0; i < 3; i++) {
        a_oppo = i;
        if (dm_a.count(a_oppo) > 0) {
            continue;
        }
        for (int j = 0; j < 3; j++) {
            b_oppo = j;
            if (b_oppo == a_oppo) {
                continue;
            }
            c_oppo = 3 - a_oppo - b_oppo;
            if (dm_c.count(c_oppo) > 0) {
                continue;
            }
            found = true;
            break;
        }
        if (found) {
            break;
        }
    }
    printf(
        "order is a--%c\tb--%c\tc--%c\n", 
        names[a_oppo], names[b_oppo], names[c_oppo]
    );

    return 0;
}