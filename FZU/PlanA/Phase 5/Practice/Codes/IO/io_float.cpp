// #define CASE 1
#include <cassert>
#include <sstream> // 必须包含
#include <iostream>
using namespace std;

#if CASE == 1
string input_str = "0.0012345 3\n";
string output_str_expected = "       0.001\n     1.235e-03\n";
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
    double num1;
    int num2;
    cin >> num1 >> num2;
    char buff[256];

    // 科学计数法舍入
    double factor = pow(10.0, num2);
    int exp = (num1 == 0) ? 0 : (int)floor(log10(fabs(num1)));
    double mant = num1 * pow(10.0, -exp); // 尾数在 [1,10) 或 (-10,-1]
    double mant_scaled = mant * factor;
    // 向上微调一个最小单位，确保边界值进位
    mant_scaled = nextafter(mant_scaled, mant_scaled + 1.0);
    double mant_rounded = round(mant_scaled) / factor;
    double sci = mant_rounded * pow(10.0, exp);

    string template_string = "%12." + to_string(num2) + "f\n%14." + to_string(num2) + "e\n";
    snprintf(buff, 256, template_string.c_str(), num1, sci);
    string output_str = buff;
    cout << output_str;
#ifdef CASE
    string output_str_actual = oss.str();
    assert(output_str_actual == output_str_expected);
    cout.rdbuf(old_cout);
    cout << output_str_actual;
#endif
    return 0;
}