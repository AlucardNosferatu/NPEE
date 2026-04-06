#include <iostream>
#include <cstring>
#include <cassert>
using namespace std;

int ans[14]; // 缓存结果，初始为0

// 判断给定 k 和 m 是否满足条件
bool check(int k, int m)
{
    int n = 2 * k; // 当前总人数
    int pos = 0;   // 当前起始位置（0-index）

    // for (int i = 0; i < k - 1; ++i)
    // BUG 1：只循环 k - 1 次，漏杀最后一个坏人
    // 应修改为:
    for (int i = 0; i < k; ++i)
    {
        bool check = false;
        if (i == 0)
        {
            check = true;
        }
        // pos = (pos + m) % n;
        // BUG 2: 报数多1，实际报了m+1
        // 应修改为:
        pos = (pos + m - 1) % n;
        if (check)
        {
            // 报数5次：0 1 2 3 4
            // 也就是m-1
            assert(pos == (m - 1) % n);
        }
        if (pos < k)
            return false; // 杀到了好人
        n--;              // 移除坏人，人数减1
        // 移除后，下一个起始位置自动为 pos（因为后面的人前移了）
    }
    assert(n <= k);
    return true; // 由于循环少一次，可能误判
}

// 计算第 k 组对应的最小 m
int compute(int k)
{
    // 从 m = k+1 开始枚举
    bool first = true;
    for (int m = k + 1;; ++m)
    {
        if (first)
        {
            first = false;
            assert(m == k + 1);
        }
        if (check(k, m))
            return m;
    }
}

int main()
{
    int k;
    while (cin >> k && k)
    {
        if (ans[k] == 0)
        { // 首次遇到，计算并缓存
            ans[k] = compute(k);
        }
        cout << ans[k] << endl;
    }
    return 0;
}