#define CASE 6
#include <cassert>
#include <iostream>
#include <vector>
#include <algorithm>
#include <sstream>
#include <string>
#include <set>
using namespace std;

#ifdef CASE
int input_idx = 0;
int output_idx = 0;
bool cin_ref;
#else
istream &cin_ref = cin;
#endif

#if CASE == 1
vector<int> vector_x = {1, 2, 3, 0, 7, 4, 0, 1, 1, 0, 6, 2, 3, 0};
vector<string> vector_y = {
    "7 (3): 1 1 2 3\n", "4 (2): 1 3\n",
    "6 ---- none\n", "2 (2): 1 1\n", "3 (2): tie\n"};
#elif CASE == 2
vector<int> vector_x = {1, 2, 0, 2, 0, 0};
vector<string> vector_y = {
    "2 (2): 1 2\n"};
#elif CASE == 3
vector<int> vector_x = {1, 2, 3, 4, 0, 10, 0, 0};
vector<string> vector_y = {
    "10 (4): 1 2 3 4\n"};
#elif CASE == 4
vector<int> vector_x = {3, 5, 0, 1, 0, 0};
vector<string> vector_y = {
    "1 ---- none\n"};
#elif CASE == 5
vector<int> vector_x = {5, 6, 0, 11, 0, 0};
vector<string> vector_y = {
    "11 (2): tie\n"};
#elif CASE == 6
vector<int> vector_x = {2, 3, 4, 0, 7, 0, 0};
vector<string> vector_y = {
    "7 (2): 3 4\n"};
#endif

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
        // Bug2: 最大面值比较方向错误（应该大的好，这里改成小的好）
        return maxVal < other.maxVal; // 错误：应 return maxVal > other.maxVal;
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
        // Bug1: 类型计数错误（按面值去重，而不是按索引）
        set<int> uniqueVals; // 用于统计不同面值
        int maxVal = 0;
        for (int i = 0; i < n; ++i)
        {
            if (curCount[i] > 0)
            {
                for (int k = 0; k < curCount[i]; ++k)
                    list.push_back(stamps[i]);
                uniqueVals.insert(stamps[i]);
                if (stamps[i] > maxVal)
                    maxVal = stamps[i];
            }
        }
        int types = uniqueVals.size(); // 错误：相同面值只算一种
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

int input_router()
{
    int temp;
#ifdef CASE
    temp = vector_x[input_idx];
    input_idx++;
    cin_ref = (input_idx < vector_x.size());
#else
    cin >> temp;
#endif
    return temp;
}

string build_output(int d, string best_type, string best_stamps)
{
    string output = to_string(d) + " " + best_type + " " + best_stamps + "\n";
    return output;
}
int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int x;
    bool first = true;

    x = input_router();

    while (cin_ref)
    {
#pragma region
        // 读取邮票序列，直到0
        stamps.clear();
        if (x == 0)
            break; // 可能没有邮票？但按题意不会
        stamps.push_back(x);
        x = input_router();
        while (cin_ref && x != 0)
        {
            stamps.push_back(x);
            x = input_router();
        }
        int n = stamps.size();
        // 读取需求序列，直到0
        vector<int> demands;

        x = input_router();
        while (cin_ref && x != 0)
        {
            demands.push_back(x);
            x = input_router();
        }
#pragma region
        // 处理每个需求
        string output_buffer;
        for (int d : demands)
        {
            solutions.clear();
            curCount.assign(n, 0);
            dfs(0, 0, 0, d, n);
            if (solutions.empty())
            {
                output_buffer = build_output(d, "----", "none");
#ifdef CASE
                assert(output_buffer == vector_y[output_idx]);
                output_idx++;
#endif
                cout << output_buffer;
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
                    output_buffer = build_output(
                        d,
                        "(" + to_string(best.types) + "):",
                        "tie");
#ifdef CASE
                    assert(output_buffer == vector_y[output_idx]);
                    output_idx++;
#endif
                    cout << output_buffer;
                }
                else
                {
                    string bs_string = "";
                    for (int v : best.stamps)
                        bs_string = bs_string + to_string(v) + " ";
                    bs_string.pop_back();
                    output_buffer = build_output(
                        d,
                        "(" + to_string(best.types) + "):",
                        bs_string);
                    cout << output_buffer;
#ifdef CASE
                    assert(output_buffer == vector_y[output_idx]);
                    output_idx++;
#endif
                }
            }
        }
#pragma endregion
#pragma endregion
        x = input_router();
    }
    return 0;
}
