#include <iostream>
#include <cstring>
#include <vector>
#include <cassert>
using namespace std;

int main()
{
    int a[7];
    int caseNum = 1;
    while (true)
    {
        // 输入所有大理石的价值，记录并计算总和
        // 方法是给价值计数
        int sum = 0;
        for (int i = 1; i <= 6; ++i)
        {
            cin >> a[i];
            sum += a[i] * i;
        }

        if (sum == 0)
            break;

        cout << "Collection #" << caseNum++ << ":" << endl;
        // 如果总价值是奇数，那就免谈了
        if (sum % 2 != 0)
        {
            cout << "Can't be divided." << endl
                 << endl;
            continue;
        }

        // 如果总价值是偶数，那就看每个人应当拿到多少作为target
        int target = sum / 2;
        vector<bool> dp;
        for (int z = 0; z < target + 1; z++)
        {
            dp.push_back(false);
        }
        // 都不分配天然可行
        dp[0] = true;

        // 0-N背包问题
        for (int i = 1; i <= 6; ++i)
        {
            if (a[i] == 0)
                continue;
            int num = a[i];
            // 🐛 BUG 1：应为 k = 1，导致二进制拆分丢失 1 份物品
            // int k = 2;
            // 应该为：
            int k = 1;
            // 从低价值的开始遍历，用完一种价值的石头再换下一种价值的
            bool check1 = (i == 1);
            while (num > 0)
            {
                // 需要拿k个石头，num不够k就只能拿num个
                int use = min(k, num);
                // 计算拿出石头的总价值（当做一个物品）
                int val = use * i;
                bool check2 = (i == 1) && (val == 1) && (target > 1);
                // 🐛 BUG 2：内层循环方向错误（应为从 target 向下），导致完全背包
                // for (int j = val; j <= target; ++j)
                // 应改为：
                for (int j = target; j >= val; --j)
                {
                    // 关键转移方程
                    // 如果目标j-val的分配方案可行，那么目标j的也可行，因为直接填上val就行了
                    if (dp[j - val])
                        dp[j] = true;
                }
                if (check2)
                {
                    // 断言确定val=1时的单坨物品群是不可能满足target>=2的情况
                    // 如果dp更新顺序错误，会导致当前物品的小容量为大容量提供了不应存在的可行性前提
                    assert(!dp[target]);
                }
                num -= use;
                k <<= 1;
            }
            if (check1)
            {
                for (int j = a[i]; j >= 0; j--)
                {
                    // 当石头价值1的时候，理论上该类石头总数a[i]以内的可行性都是能够满足的
                    // 检测到的bug失去1这个二进制分解起点，会导致凑出的石头群数量总是偶数，只能满足偶数目标的可行性
                    assert(dp[j]);
                }
            }
        }
        if (dp[target])
            cout << "Can be divided." << endl;
        else
            cout << "Can't be divided." << endl;
        cout << endl;
    }
    return 0;
}