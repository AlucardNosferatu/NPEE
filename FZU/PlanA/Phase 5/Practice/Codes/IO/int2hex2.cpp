// #define CASE 1
#include <cassert>
#include <iostream>
#include <vector>
using namespace std;

#if CASE == 1
int a_case = 4095;
int b_case = 8;
string c_case = "0FFF\n00010\n  4103\n";
#else
int a_case;
int b_case;
string c_case;
#endif

int main()
{
    char buff[256];
    string output;
    int a, b, c;
#ifdef CASE
    a = a_case;
    b = b_case;
#else
    cin >> a >> b;
#endif
    c = a + b;
    snprintf(buff, 256, "%04X\n%05o\n%6d\n", a, b, c);
    output = buff;
#ifdef CASE
    assert(output == c_case);
#endif
    cout << output;
    return 0;
}