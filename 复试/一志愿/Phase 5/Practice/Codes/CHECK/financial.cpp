#include <iostream>
#include <iomanip>
#include <cassert>
#include <cmath>
using namespace std;

int main()
{
    double sum = 0.0;
    double x;
    int count = 0;
    for (int i = 0; i < 12; ++i)
    // 🐛 BUG 1：循环只进行11次，应为12次
    {
        cin >> x;
        sum += x;
        count++;
    }
    assert(count == 12);
    double avg = sum / 12.0;
    // 🐛 BUG 2：除以11.0，应为12.0
    assert(fabs(avg * 12.0 - sum) < 1e-6);
    cout << fixed << setprecision(2) << "$" << avg << endl;
    return 0;
}