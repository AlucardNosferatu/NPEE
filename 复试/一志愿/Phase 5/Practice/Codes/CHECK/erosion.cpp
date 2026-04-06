#include <iostream>
#include <cmath>
#include <iomanip>
#include <cassert>
#include <string>
using namespace std;

string build_output_string(int i, int year)
{
    string output;
    const string prop_prefix = "Property ";
    const string prop_suffix = ": This property will begin eroding in year ";
    output = prop_prefix + to_string(i) + prop_suffix + to_string(year) + ".\n";
    // 漏了末尾的英文句号（"."）和换行符（"\n"）
    return output;
}

int calculate_year(double x, double y)
{
    const double PI = 3.14;
    double r_square = x * x + y * y;
    int year = ceil(PI * r_square / 100.0);
    // 半圆面积50平方英里，对应全圆是100平方英里
    // 达到目标圆面积PI *r_square需要PI *r_square / 100.0年
    return year;
}

int main()
{
    string output;
    int year, N;
    double x, y;
    cin >> N;
    for (int i = 1; i <= N; ++i)
    {
        cin >> x >> y;
        year = calculate_year(x, y);
        assert(year >= 0);
        output = build_output_string(i, year);
        cout << output;
    }
    const string pattern_string = "Property 1: This property will begin eroding in year 1.";
    string test_string = build_output_string(1, 1);
    // assert(pattern_string.size() == test_string.size());
    for (int i = 0; i < min(pattern_string.size(), test_string.size()); i++)
    {
        assert(pattern_string.compare(0, i + 1, test_string));
    }
    cout << "END OF OUTPUT." << endl;
    return 0;
}