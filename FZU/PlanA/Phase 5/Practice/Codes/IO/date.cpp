#define CASE 1
#include <cassert>
#include <iostream>
#include <vector>
#include <stdexcept>
#include <sstream> // 必须包含
using namespace std;

#if CASE == 1
string input_case = "2000 12 31\n";
string output_case = "2000/12/31\nDay of year: 366\n";
#else
string input_case, output_case;
#endif

int main()
{
    char buff[256];
    string output;
    int year, month, day, doy;
    bool is_leap;
#ifdef CASE
    istringstream in;
    in.str(input_case);
    // 保存 cin 原来的缓冲区（可选，用于恢复）
    streambuf *orig_cin = cin.rdbuf();
    // 重定向 cin 到 in
    cin.rdbuf(in.rdbuf());
#endif
    cin >> year >> month >> day;

    is_leap = ((year % 4 == 0) && (year % 100 != 0)) || (year % 400 == 0);
    doy = 0;
    switch (month)
    {
    // 从大月份往下穿透，全部累加
    case 12:
        doy += 30;
    case 11:
        doy += 31;
    case 10:
        doy += 30;
    case 9:
        doy += 31;
    case 8:
        doy += 31;
    case 7:
        doy += 30;
    case 6:
        doy += 31;
    case 5:
        doy += 30;
    case 4:
        doy += 31;
    case 3:
        doy += is_leap ? 29 : 28;
    case 2:
        doy += 31;
    case 1:
        doy += 0;
        break;
    default:
        throw runtime_error("Invalid month");
        break;
    }
    doy += day;
    snprintf(buff, 256, "%04d/%02d/%02d\nDay of year: %03d\n", year, month, day, doy);
    output = buff;
#ifdef CASE
    assert(output == output_case);
#endif
    cout << output;
    return 0;
}