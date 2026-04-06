#define CASE 1

#include <iostream>
#include <vector>
#include <algorithm>
#include <sstream>
#include <string>
#include <cassert>
using namespace std;

struct Solution
{
    vector<int> stamps; // 所选邮票的面值（已排序）
    int types;          // 不同种类的数量
    int total;          // 总张数
    int maxVal;         // 最大面值

    Solution() : types(0), total(0), maxVal(0) {}
    Solution(const vector<int> &s, int t, int tot, int m)
        : stamps(s), types(t), total(tot), maxVal(m) {}

    // 比较两个解，返回 true 如果当前解优于 other
    bool betterThan(const Solution &other) const
    {
        if (types != other.types)
            return types > other.types;
        if (total != other.total)
            return total < other.total;
        return maxVal > other.maxVal;
    }

    // 判断是否与另一个解完全相同（用于平局）
    bool equalTo(const Solution &other) const
    {
        return types == other.types && total == other.total && maxVal == other.maxVal;
    }
};

vector<int> stamps;         // 所有邮票面值（可能有重复）
vector<int> curCount;       // 当前递归中每种邮票的使用数量
vector<Solution> solutions; // 存放当前需求的所有合法解

void dfs(int idx, int cnt, int sum, int target, int n)
{
    if (cnt > 4 || sum > target)
        return;
    if (sum == target)
    {
        // 找到一个合法解
        vector<int> list;
        int types = 0;
        int maxVal = 0;
        for (int i = 0; i < n; ++i)
        {
            if (curCount[i] > 0)
            {
                types++;
                for (int k = 0; k < curCount[i]; ++k)
                    list.push_back(stamps[i]);
                if (stamps[i] > maxVal)
                    maxVal = stamps[i];
            }
        }
        sort(list.begin(), list.end());
        solutions.emplace_back(list, types, cnt, maxVal);
        return;
    }
    if (idx >= n)
        return;
    // 尝试取 0 到 4 张当前邮票
    for (int k = 0; k <= 4 - cnt; ++k)
    {
        curCount[idx] = k;
        dfs(idx + 1, cnt + k, sum + k * stamps[idx], target, n);
    }
    curCount[idx] = 0; // 恢复
}

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

#ifdef CASE // 所有测试模式通用的部分
// ---------- 根据不同的 CASE 值选择输入数据和预期输出 ----------
#if CASE == 1
    // 测试用例集1：对应 stamp.cpp 中的测试数据
    vector<int> input_data = {1, 2, 3, 0, 7, 4, 0, 1, 1, 0, 6, 2, 3, 0};
    vector<string> expected = {
        "7 (3): 1 1 2 3\n",
        "4 (2): 1 3\n",
        "6 ---- none\n",
        "2 (2): 1 1\n",
        "3 (2): tie\n"};
#elif CASE == 2
    // TODO: 请在此填入第二组测试数据
    vector<int> input_data;  // 需要用户填充
    vector<string> expected; // 需要用户填充
#error "Please define input_data and expected for CASE=2"
#elif CASE == 3
    // TODO: 请在此填入第三组测试数据
    vector<int> input_data;  // 需要用户填充
    vector<string> expected; // 需要用户填充
#error "Please define input_data and expected for CASE=3"
#else
#error "Unsupported CASE value (only 1,2,3 are supported)"
#endif

    // 将 input_data 转换为字符串，并绑定到 cin
    ostringstream oss;
    for (size_t i = 0; i < input_data.size(); ++i)
    {
        if (i > 0)
            oss << ' ';
        oss << input_data[i];
    }
    string input_str = oss.str();
    istringstream iss(input_str);
    cin.rdbuf(iss.rdbuf());

    size_t expected_idx = 0; // 用于逐行断言
#endif

    int x;
    while (cin >> x)
    {
        // 读取邮票序列，直到0
        stamps.clear();
        if (x == 0)
            break; // 可能没有邮票？但按题意不会
        stamps.push_back(x);
        while (cin >> x && x != 0)
        {
            stamps.push_back(x);
        }
        int n = stamps.size();
        // 读取需求序列，直到0
        vector<int> demands;
        while (cin >> x && x != 0)
        {
            demands.push_back(x);
        }
        // 处理每个需求
        for (int d : demands)
        {
            solutions.clear();
            curCount.assign(n, 0);
            dfs(0, 0, 0, d, n);
            if (solutions.empty())
            {
                // 输出：无解
#ifdef CASE
                string out = to_string(d) + " ---- none\n";
                cout << out;
                assert(out == expected[expected_idx++]);
#else
                cout << d << " ---- none\n";
#endif
            }
            else
            {
                // 找出最佳解
                Solution best = solutions[0];
                bool tie = false;
                for (size_t i = 1; i < solutions.size(); ++i)
                {
                    if (solutions[i].betterThan(best))
                    {
                        best = solutions[i];
                        tie = false;
                    }
                    else if (!best.betterThan(solutions[i]) && best.equalTo(solutions[i]))
                    {
                        tie = true;
                    }
                }
                // 再次检查是否有多个与best相等的解（因为可能有多个同优）
                if (!tie)
                {
                    int countBest = 0;
                    for (auto &sol : solutions)
                    {
                        if (sol.equalTo(best))
                            countBest++;
                    }
                    if (countBest > 1)
                        tie = true;
                }
                if (tie)
                {
                    // 输出：平局
#ifdef CASE
                    string out = to_string(d) + " (" + to_string(best.types) + "): tie\n";
                    cout << out;
                    assert(out == expected[expected_idx++]);
#else
                    cout << d << " (" << best.types << "): tie\n";
#endif
                }
                else
                {
                    // 输出：最佳解
#ifdef CASE
                    string out = to_string(d) + " (" + to_string(best.types) + "):";
                    for (int v : best.stamps)
                    {
                        out += " " + to_string(v);
                    }
                    out += "\n";
                    cout << out;
                    assert(out == expected[expected_idx++]);
#else
                    cout << d << " (" << best.types << "):";
                    for (int v : best.stamps)
                        cout << ' ' << v;
                    cout << '\n';
#endif
                }
            }
        }
    }
    return 0;
}