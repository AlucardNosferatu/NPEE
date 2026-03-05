// 1016 - 数字的自我描述 (带2个边界bug)
// 测试模式信号（宏开启时提交）：
//   WA = 用例通过（未触发bug），程序正常结束，输出结果（与OJ数据不符）
//   RE = 用例触发bug，断言失败，程序崩溃
// 本地测试：取消注释 #define CASE 1（或2），修改对应分支的测试数据，运行即可。

#define CASE 6 // 默认关闭，测试时取消注释

#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <cassert>
using namespace std;

// 计算库存字符串（bug1：忽略数字0的计数）
string inventory(const string &s)
{
    int cnt[10] = {0};
    for (char c : s)
    {
        cnt[c - '0']++;
    }
    string res;
    // bug: 循环从1开始，跳过数字0
    for (int d = 1; d <= 9; d++)
    // for (int d = 0; d <= 9; d++)
    { // 原本应为 d = 0
        if (cnt[d] > 0)
        {
            res += to_string(cnt[d]) + char('0' + d);
        }
    }
    // 特殊处理数字0？这里完全忽略了0，所以当数字包含0时，0的计数不会出现在库存中
    // 例如 "0" 的库存将变成空字符串，导致后续迭代异常
    return res;
}

int main()
{
#ifdef CASE
    // ========== 测试模式：准备硬编码输入与预期输出 ==========
    string test_input, expected_output;
#if CASE == 1
    // 请在此处填入你的测试用例（输入）和预期输出
    test_input = "22\n31123314\n314213241519\n21221314\n111222234459\n-1\n";
    expected_output = "22 is self-inventorying\n31123314 is self-inventorying\n314213241519 enters an inventory loop of length 2\n21221314 is self-inventorying after 2 steps\n111222234459 enters an inventory loop of length 2\n";
#elif CASE == 2
    // 预留其他用例集
    test_input = "0\n-1\n";
    expected_output = "0 is self-inventorying after 10 steps\n"; // 实际应输出？0的迭代会是什么？
#elif CASE == 3
    test_input = "22\n-1\n";
    expected_output = "22 is self-inventorying\n";
#elif CASE == 4
    test_input = "11\n-1\n";
    expected_output = "11 is self-inventorying after 11 steps\n";
#elif CASE == 5
    test_input = "1000000000000\n-1\n";
    expected_output = "1000000000000 is self-inventorying after 8 steps\n";
#elif CASE == 6
    test_input = "1234567890\n-1\n";
    expected_output = "1234567890 is self-inventorying after 4 steps\n";
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

    // ========== 核心逻辑（含bug2：循环长度减1） ==========
    string n;
    while (cin >> n)
    {
        if (n == "-1")
            break;

        vector<string> seq;
        seq.push_back(n);
        for (int i = 1; i <= 15; i++)
        {
            seq.push_back(inventory(seq.back()));
        }

        bool found = false;
        for (int i = 0; i <= 15; i++)
        {
            // 检查自描述（包括经过j步）
            if (i + 1 <= 15 && seq[i] == seq[i + 1])
            {
                if (i == 0)
                    cout << n << " is self-inventorying" << endl;
                else
                    cout << n << " is self-inventorying after " << i << " steps" << endl;
                found = true;
                break;
            }
            // 检查循环（长度≥2）
            for (int j = i + 2; j <= 15; j++)
            {
                if (seq[i] == seq[j])
                {
                    // bug2：循环长度错误地减1
                    cout << n << " enters an inventory loop of length " << j - i - 1 << endl; // 正确应为 j - i
                    // cout << n << " enters an inventory loop of length " << j - i << endl;
                    found = true;
                    break;
                }
            }
            if (found)
                break;
        }

        if (!found)
        {
            cout << n << " can not be classified after 15 iterations" << endl;
        }
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