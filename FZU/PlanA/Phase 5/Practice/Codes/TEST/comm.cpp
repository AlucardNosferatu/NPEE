// 1018 - 通信系统 (带2个边界bug)
// 测试模式信号（宏开启时提交）：
//   WA = 用例通过（未触发bug），程序正常结束，输出结果（与OJ数据不符）
//   RE = 用例触发bug，断言失败，程序崩溃
// 本地测试：取消注释 #define CASE 1（或2），修改对应分支的测试数据，运行即可。

#define CASE 8 // 默认关闭，测试时取消注释

#include <iostream>
#include <vector>
#include <algorithm>
#include <sstream>
#include <iomanip>
#include <cassert>
#include <set>
#include <cmath>
using namespace std;

int main()
{
#ifdef CASE
    // ========== 测试模式：准备硬编码输入与预期输出 ==========
    string test_input, expected_output;
#if CASE == 1
    // 样例数据
    test_input = "1\n3\n3 100 25 150 35 80 25\n2 120 80 155 40\n2 100 100 120 110\n";
    expected_output = "0.649\n";
#elif CASE == 2
    // 预留其他用例集（用户可自行添加）
    test_input = "1\n1\n2 10 5 20 8\n";
    expected_output = "2.500\n";
#elif CASE == 3
    // 预留其他用例集（用户可自行添加）
    test_input = "1\n1\n1 100 50\n";
    expected_output = "2.000\n";
#elif CASE == 4
    // 预留其他用例集（用户可自行添加）
    test_input = "1\n1\n3 100 50 200 100 300 150\n";
    expected_output = "2.000\n";
#elif CASE == 5
    // 预留其他用例集（用户可自行添加）
    test_input = "1\n2\n1 100 50\n1 80 30\n";
    expected_output = "1.000\n";
#elif CASE == 6
    // 预留其他用例集（用户可自行添加）
    test_input = "1\n2\n2 100 10 200 20\n2 150 15 250 25\n";
    expected_output = "4.444\n";
#elif CASE == 7
    // 预留其他用例集（用户可自行添加）
    test_input = "1\n3\n1 100 1\n2 200 2 300 3\n3 400 4 500 5 600 6\n";
    expected_output = "14.286\n";
#elif CASE == 8
    // 预留其他用例集（用户可自行添加）
    test_input = "1\n1\n1 1000000 1\n";
    expected_output = "1000000.000\n";
#else
#error "Unsupported CASE value"
#endif
    // 重定向输入流
    istringstream iss(test_input);
    cin.rdbuf(iss.rdbuf());

    // 重定向输出流到字符串流，以便捕获结果
    ostringstream oss;
    streambuf *old_cout = cout.rdbuf(oss.rdbuf());
#endif

    // ========== 核心逻辑（含2个边界bug） ==========
    int t;
    cin >> t;
    while (t--)
    {
        int n;
        cin >> n;
        vector<vector<pair<int, int>>> devices(n);
        set<int> bandwidths;
        for (int i = 0; i < n; ++i)
        {
            int m;
            cin >> m;
            devices[i].resize(m);
            for (int j = 0; j < m; ++j)
            {
                int b, p;
                cin >> b >> p;
                devices[i][j] = {b, p};
                bandwidths.insert(b);
            }
        }
        double best = 0.0;
        // 枚举每个可能的带宽作为B
        for (int B : bandwidths)
        {
            int total_price = 0;
            bool ok = true;
            for (int i = 0; i < n; ++i)
            {
                int min_price = 1e9;
                for (size_t k = 0; k < devices[i].size(); ++k)
                {
                    int b = devices[i][k].first;
                    int p = devices[i][k].second;
                    // bug1: 条件由 b >= B 改为 b > B（严格大于）
                    if (b > B && p < min_price)
                    { // 正确应为 b >= B
                        min_price = p;
                    }
                }
                if (min_price == 1e9)
                {
                    ok = false;
                    break;
                }
                total_price += min_price;
            }
            if (ok)
            {
                double cur = (double)B / total_price;
                if (cur > best)
                    best = cur;
            }
        }

        // bug2: 错误地向下取整到三位小数（而不是四舍五入）
        best = floor(best * 1000 + 1e-9) / 1000; // 正确应为直接输出

        // 输出固定三位小数
        cout << fixed << setprecision(3) << best << endl;
    }

#ifdef CASE
    // ========== 测试模式：捕获输出、断言、恢复并输出结果 ==========
    string result = oss.str();
    cout.rdbuf(old_cout);

    // 单次断言：失败则触发RE，成功则继续
    assert(result == expected_output);

    // 断言通过后输出结果（OJ判WA）
    cout << result;
#endif

    return 0;
}