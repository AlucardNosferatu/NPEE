#define CASE 1
#include <cassert>
#include <sstream> // 必须包含
#include <iostream>
#include <vector>
using namespace std;

#if CASE == 1
string input_str = "4 4\n1 2 3 4\n5 6 7 8\n9 10 11 12\n13 14 15 16\n";
string output_str_expected = "     1     2     3     4\n     5     6     7     8\n     9    10    11    12\n    13    14    15    16\n";
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
    int row, col, temp;
    vector<vector<int>> mat;
    char buff[256];
    string temp_str;
    string output_str = "";
    cin >> row >> col;
    for (int i = 0; i < row; i++)
    {
        vector<int> mat_row;
        for (int j = 0; j < col; j++)
        {
            cin >> temp;
            snprintf(buff, 256, "%6d", temp);
            temp_str = buff;
            output_str = output_str + temp_str;
            mat_row.push_back(temp);
        }
        mat.push_back(mat_row);
        output_str = output_str + "\n";
    }
    cout << output_str;
#ifdef CASE
    string output_str_actual = oss.str();
    assert(output_str_actual == output_str_expected);
    cout.rdbuf(old_cout);
    cout << output_str_actual;
#endif
    return 0;
}