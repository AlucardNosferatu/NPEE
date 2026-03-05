#include <iostream>
#include <cassert>
#include <string>
using namespace std;

string build_output_string(int caseNum, int days)
{
    string output = "Case " + to_string(caseNum) + ": the next triple peak occurs in " + to_string(days) + " days.";
    return output;
}

int countdown(int p, int e, int i, int d)
{
    int day;
    for (day = d + 1; day <= d + 21252; ++day)
    // 从下一天开始的下一个三花聚顶日，如果当天是三花聚顶日，不能算在内
    {
        if ((day - p) % 23 == 0 && (day - e) % 28 == 0 && (day - i) % 33 == 0)
        {
            break;
        }
    }
    return day - d;
}

int main()
{
    int p, e, i, d, days, days_test;
    int caseNum = 1;
    string output;
    while (cin >> p >> e >> i >> d)
    {
        if (p == -1 && e == -1 && i == -1 && d == -1)
            break;

        days = countdown(p, e, i, d);

        output = build_output_string(caseNum, days);
        cout << output << endl;
        caseNum++;
    }
    days_test = countdown(10, 5, 0, 33);
    assert(days_test != 0);
    // const string pattern_string = "Case 1: the next triple peak occurs in 21252 days.";
    // string test_string = build_output_string(1, 21252);
    // assert(pattern_string == test_string);
    return 0;
}