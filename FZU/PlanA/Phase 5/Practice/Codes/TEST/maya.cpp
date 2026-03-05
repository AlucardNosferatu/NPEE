#define CASE 1
#include <cassert>
#include <iostream>
#include <string>
#include <vector>
#include <map>
using namespace std;

string build_answer(int tzolkinNumber, string tzolkinNames, int tzolkinYear)
{
    string answer = to_string(tzolkinNumber) + " " + tzolkinNames + " " + to_string(tzolkinYear);
    return answer;
}

int main()
{
    string answer;
    // 月份名称映射
    string haabMonths[19] = {
        "pop", "no", "zip", "zotz", "tzec", "xul", "yoxkin", "mol", "chen",
        "yax", "zac", "ceh", "mac", "kankin", "muan", "pax", "koyab", "cumhu",
        "uayet"};
    map<string, int> monthIndex;
    for (int i = 0; i < 19; ++i)
    {
        monthIndex[haabMonths[i]] = i;
    }
    // Tzolkin 日名称
    string tzolkinNames[20] = {
        "imix", "ik", "akbal", "kan", "chicchan", "cimi", "manik", "lamat",
        "muluk", "ok", "chuen", "eb", "ben", "ix", "mem", "cib", "caban",
        "eznab", "canac", "ahau"};
    int n;
#if CASE == 1
    // FAIL
    n = 3;
    vector<int> days = {10, 0, 10};
    vector<string> months = {"zac", "pop", "zac"};
    vector<int> years = {0, 0, 1995};
    vector<string> answers = {"3 chuen 0", "1 imix 0", "9 cimi 2801"};
#elif CASE == 2
    // FAIL
    n = 10;
    vector<int> days = {0, 19, 4, 0, 0, 10, 1, 0, 19, 0};
    vector<string> months = {"pop", "cumhu", "uayet", "pop", "kankin", "zac", "pop", "uayet", "pop", "uayet"};
    vector<int> years = {0, 0, 0, 1, 0, 1995, 0, 0, 0, 4};
    vector<string> answers = {"1 imix 0", "9 ahau 1", "1 chicchan 1", "2 cimi 1", "1 imix 1", "9 cimi 2801", "2 ik 0", "10 imix 1", "7 ahau 0", "1 imix 7"};
#elif CASE == 3
    // FAIL
    n = 5;
    vector<int> days = {0, 0, 19, 0, 4};
    vector<string> months = {"pop", "uayet", "cumhu", "pop", "uayet"};
    vector<int> years = {0, 0, 0, 1, 4999};
    vector<string> answers = {"1 imix 0", "10 imix 1", "9 ahau 1", "2 cimi 1", "8 ahau 7019"};
#else
    cin >> n;
#endif

    cout << n << endl; // 输出与输入相同的行数

    for (int i = 0; i < n; ++i)
    {
        int day, year;
        char dot;
        string month;
#ifdef CASE
        day = days[i];
        month = months[i];
        year = years[i];
#else
        cin >> day >> dot >> month >> year; // 读取如 "10. zac 0"
#endif
        int monthIdx = monthIndex[month];
        // Bug1: 总天数多加了1
        int totalDays = year * 365 + monthIdx * 20 + day + 1; // 正确应为不加1
        int tzolkinYear = totalDays / 260;
        // Bug2: Tzolkin数字没有加1（正确应为 totalDays % 13 + 1）
        int tzolkinNumber = totalDays % 13; // 错误：范围0~12
        int tzolkinNameIdx = totalDays % 20;
        answer = build_answer(tzolkinNumber, tzolkinNames[tzolkinNameIdx], tzolkinYear);
#ifdef CASE
        assert(answers[i] == answer);
#endif
        cout << answer << endl;
    }
    return 0;
}