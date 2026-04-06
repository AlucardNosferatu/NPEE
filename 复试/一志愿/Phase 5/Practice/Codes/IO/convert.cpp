#define CASE 1
#include <cassert>
#include <sstream> // 必须包含
#include <iostream>
using namespace std;

#if CASE == 1
string input_str = "4095\n";
string output_str_expected = "  4095\n FFF\n 7777\n";
#elif CASE == 2
string input_str;
string output_str_expected;
#endif

int main()
{
#ifdef CASE
    istringstream iss;
    ostringstream oss;
    iss.str(input_str);
    streambuf *old_cin = cin.rdbuf(iss.rdbuf());
    streambuf *old_cout = cout.rdbuf(oss.rdbuf());
#endif
    int num;
    cin >> num;
    char buff[256];
    string output;
    snprintf(buff, 256, "%6d\n%4X\n%5o\n", num, num, num);
    output = buff;
    cout << output;
#ifdef CASE
    string output_str_actual = oss.str();
    assert(output_str_actual == output_str_expected);
    cout.rdbuf(old_cout);
    cout << output_str_actual;
#endif
    return 0;
}