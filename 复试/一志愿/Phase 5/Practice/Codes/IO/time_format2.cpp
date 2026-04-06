// #define CASE 1
#include <cassert>
#include <iostream>
#include <vector>
#include <stdexcept>
#include <sstream> // 必须包含
using namespace std;

#if CASE == 1
string input_case = "9 5 8\n";
string output_case = "09:05:08\n09:05:08 AM\n";
#else
string input_case, output_case;
#endif

int main()
{
    char buff[256];
    string output;
    int hour, minute, second, mod_h;
    bool is_pm;
#ifdef CASE
    istringstream in;
    in.str(input_case);
    // 保存 cin 原来的缓冲区（可选，用于恢复）
    streambuf *orig_cin = cin.rdbuf();
    // 重定向 cin 到 in
    cin.rdbuf(in.rdbuf());
#endif
    cin >> hour >> minute >> second;
    mod_h = hour;
    is_pm = false;
    if (!(hour + minute + second == 0))
    { // 非 00:00:00 时
        if (hour >= 12)
        {
            is_pm = true;
            mod_h = (hour == 12) ? 12 : hour - 12;
        }
    }
    else
        mod_h = 12;
    snprintf(
        buff, 256, "%02d:%02d:%02d\n%02d:%02d:%02d %s\n",
        hour, minute, second, mod_h, minute, second,
        is_pm ? "PM" : "AM");
    output = buff;
#ifdef CASE
    assert(output == output_case);
#endif
    cout << output;
    return 0;
}