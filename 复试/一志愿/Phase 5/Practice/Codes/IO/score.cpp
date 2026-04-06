#define CASE 1
#include <cassert>
#include <sstream> // 必须包含
#include <iostream>
using namespace std;

#if CASE == 1
string input_str = "John\n59 60 61\n";
string output_str_expected = "Name:John       Math: 59 Chinese: 60 English: 61\n";
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
    string name;
    int math, chinese, english;
    cin >> name >> math >> chinese >> english;
    char buff[256];
    string output;
    snprintf(buff, 256, "Name:%-10s Math:%3d Chinese:%3d English:%3d\n", name, math, chinese, english);
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