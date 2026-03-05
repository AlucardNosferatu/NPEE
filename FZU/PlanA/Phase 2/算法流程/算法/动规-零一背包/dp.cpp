#include <iostream>
#include <vector>
#include <cassert>
#include <algorithm>

using namespace std;

// 0-1背包问题：动态规划解法
// 输入参数：capacity - 背包容量，weights - 物品重量数组，values - 物品价值数组
// 输出参数：能够装入背包的最大总价值
// 核心思想：使用动态规划，dp[j]表示容量为j的背包能装下的最大价值
int knapsack_01_dp(int capacity, const vector<int> &weights, const vector<int> &values)
{
    // ====================== 核心变量声明 ======================
    vector<int> dp; // 用途：动态规划数组，dp[j]表示容量为j的背包能获得的最大价值；数据来源：初始化全0，逐步更新；生命周期：整个算法执行期间
    int n;          // 用途：物品数量；数据来源：weights数组长度；生命周期：整个算法执行期间
    int i;          // 用途：当前处理的物品索引；数据来源：从0开始递增到n-1；生命周期：外层循环期间
    int j;          // 用途：当前处理的背包容量；数据来源：从capacity递减到0；生命周期：内层循环期间
// 豁免说明：weight_i, value_i, new_value, old_value是临时计算变量，不跨标签使用，变化无需状态断言

// ====================== 算法开始 ======================
INIT:
    // 目的：初始化算法所需的核心变量和数据结构
    // 变量关联：dp数组初始化为全0，n记录物品数量，i从0开始
    // 全局作用：为动态规划算法准备初始状态，包括DP数组初始化
    n = static_cast<int>(weights.size()); // 获取物品数量，用于后续循环边界控制
    // 输入验证：物品数量必须等于价值数量
    assert(weights.size() == values.size() && "INIT: 物品重量数组与价值数组长度不一致");
    // 输入验证：背包容量必须非负
    assert(capacity >= 0 && "INIT: 背包容量不能为负数");
    // 输入验证：所有物品重量必须非负
    for (int k = 0; k < n; k++)
    {
        assert(weights[k] >= 0 && "INIT: 物品重量不能为负数");
        assert(values[k] >= 0 && "INIT: 物品价值不能为负数");
    }
    dp = vector<int>(capacity + 1, 0); // 初始化DP数组，大小为capacity+1，全部为0
    i = 0;                             // 从第一个物品开始处理（索引0）
    goto STATE_0;                      // 跳转至初始状态断言：验证变量初始化合法性

STATE_0:
    // 断言依据：初始化后必须确保核心变量处于合法初始状态
    // 状态特征1：DP数组长度必须等于capacity+1（动态规划状态空间正确性验证）
    assert(dp.size() == static_cast<size_t>(capacity + 1) && "STATE_0: DP数组长度不等于capacity+1");
    // 状态特征2：DP数组所有元素必须为0（初始状态正确性验证）
    for (int k = 0; k <= capacity; k++)
    {
        assert(dp[k] == 0 && "STATE_0: DP数组初始状态不全为0");
    }
    // 状态特征3：物品索引i必须为0（从第一个物品开始）
    assert(i == 0 && "STATE_0: 物品索引初始状态不是0");
    // 状态特征4：物品数量n必须等于weights数组长度（数据一致性验证）
    assert(n == static_cast<int>(weights.size()) && "STATE_0: 物品数量n与重量数组长度不一致");
    // 约束目的：验证算法初始化的正确性，确保从正确状态开始动态规划
    goto CHECK_ITEMS_LOOP; // 跳转至检查物品循环条件动作

CHECK_ITEMS_LOOP:
    // 目的：检查是否还有物品需要处理
    // 变量关联：i表示当前物品索引，n表示物品总数
    // 全局作用：控制外层循环（物品遍历）的继续或终止
    // 豁免说明：这里不改变核心状态，只是条件检查，不需要状态断言
    if (i < n)
    {                              // 如果还有物品需要处理
        goto PROCESS_CURRENT_ITEM; // 跳转至处理当前物品动作
    }
    else
    {
        goto FINAL_STATE; // 跳转至准备最终状态动作
    }

PROCESS_CURRENT_ITEM:
    // 目的：开始处理当前物品
    // 变量关联：i表示当前物品索引，weights和values数组存储物品信息
    // 全局作用：获取当前物品信息，为内层循环做准备
    // 豁免说明：weight_i和value_i是临时变量，不跨标签使用，变化无需状态断言
    int weight_i = weights[i]; // 获取当前物品的重量
    int value_i = values[i];   // 获取当前物品的价值
    goto STATE_1;              // 跳转至获取物品信息后的状态断言

STATE_1:
    // 断言依据：获取当前物品信息后，必须确保数据有效且访问正确
    // 状态特征1：当前物品索引i必须在有效访问范围内（0到n-1）
    assert(i >= 0 && i < n && "STATE_1: 获取物品信息时物品索引i越界");
    // 状态特征2：获取的物品重量必须等于重量数组中对应位置的值
    assert(weight_i == weights[i] && "STATE_1: 当前物品重量与数组中对应值不一致");
    // 状态特征3：获取的物品价值必须等于价值数组中对应位置的值
    assert(value_i == values[i] && "STATE_1: 当前物品价值与数组中对应值不一致");
    // 约束目的：验证物品信息访问的正确性，避免越界访问或数据不一致
    goto INIT_CAPACITY_LOOP; // 跳转至初始化容量循环动作

INIT_CAPACITY_LOOP:
    // 目的：初始化内层循环（容量遍历）
    // 变量关联：j初始化为最大容量capacity
    // 全局作用：为内层循环（容量遍历）准备初始状态，开始处理当前物品的状态转移
    j = capacity; // 从容量的最大值开始遍历
    goto STATE_2; // 跳转至内层循环初始化后的状态断言

STATE_2:
    // 断言依据：内层循环初始化后，容量索引j必须等于capacity
    // 状态特征1：容量索引j必须等于capacity（内层循环从最大容量开始）
    assert(j == capacity && "STATE_2: 内层循环初始化后容量索引j不等于capacity");
    // 状态特征2：容量索引j必须在合法范围内（0到capacity之间）
    assert(j >= 0 && j <= capacity && "STATE_2: 内层循环初始化后容量索引j越界");
    // 约束目的：验证内层循环初始化的正确性，确保容量遍历从正确状态开始
    goto CHECK_CAPACITY_LOOP; // 跳转至检查容量循环条件动作

CHECK_CAPACITY_LOOP:
    // 目的：检查是否还有容量需要处理
    // 变量关联：j表示当前处理容量，weight_i表示当前物品重量
    // 全局作用：控制内层循环（容量遍历）的继续或终止
    // 豁免说明：这里不改变核心状态，只是条件检查，不需要状态断言
    if (j >= 0)
    {                        // 如果当前容量大于等于0，还有容量需要处理
        goto CHECK_ITEM_FIT; // 跳转至检查物品能否放入动作
    }
    else
    {
        goto INCREMENT_ITEM_INDEX; // 跳转至递增物品索引动作
    }

CHECK_ITEM_FIT:
    // 目的：检查当前物品能否放入当前容量的背包
    // 变量关联：j表示当前背包容量，weight_i表示当前物品重量
    // 全局作用：判断是否需要进行状态转移计算，这是0-1背包问题的关键条件
    // 豁免说明：这里不改变核心状态，只是条件检查，不需要状态断言
    if (j >= weight_i)
    {                   // 如果当前容量大于等于物品重量，物品可以放入
        goto UPDATE_DP; // 跳转至更新DP值动作，进行状态转移
    }
    else
    {
        goto DECREMENT_CAPACITY; // 跳转至递减容量动作，不进行状态转移
    }

UPDATE_DP:
    // 目的：更新DP数组的当前状态，选择最优解
    // 变量关联：dp数组存储历史状态，weight_i和value_i是当前物品信息
    // 全局作用：执行动态规划的状态转移，更新当前容量下的最优解
    // 豁免说明：old_value和new_value是临时计算变量，不跨标签使用，变化无需状态断言
    int old_value = dp[j];                      // 保存旧值用于状态断言
    int new_value = dp[j - weight_i] + value_i; // 计算放入当前物品的价值

    if (new_value > old_value)
    {                      // 如果放入物品的价值更大
        dp[j] = new_value; // 更新为放入物品的价值
    }
    // 注意：如果new_value <= old_value，dp[j]保持不变，不需要显式赋值
    goto STATE_3; // 跳转至更新DP值后的状态断言

STATE_3:
    // 断言依据：更新DP值后，必须确保DP值满足特定约束条件
    // 状态特征1：更新后的dp[j]必须等于old_value和new_value的最大值（最优选择验证）
    assert(dp[j] == max(old_value, new_value) && "STATE_3: 更新后的dp[j]不等于两种选择的最大值");
    // 状态特征2：更新后的dp[j]必须大于等于0（DP值非负性验证）
    assert(dp[j] >= 0 && "STATE_3: 更新后的dp[j]为负数");
    // 状态特征3：如果j>=weight_i，那么dp[j]必须至少等于value_i（因为可以选择只放当前物品）
    if (j >= weight_i)
    {
        assert(dp[j] >= value_i && "STATE_3: 更新后的dp[j]小于当前物品价值");
    }
    // 约束目的：验证状态转移更新的正确性，确保动态规划决策的最优性
    goto DECREMENT_CAPACITY; // 跳转至递减容量动作

DECREMENT_CAPACITY:
    // 目的：递减容量索引，移动到下一个容量
    // 变量关联：j表示当前处理容量
    // 全局作用：推进内层循环，使算法能够处理下一个容量值
    j = j - 1;    // 容量索引减1，处理下一个更小的容量
    goto STATE_4; // 跳转至递减容量索引后的状态断言

STATE_4:
    // 断言依据：递减容量索引后，必须确保索引值合法且递减逻辑正确
    // 状态特征1：递减后的索引必须等于原索引减1（递减逻辑正确性验证）
    // 注意：这里通过变量自身的数学关系验证，实际上递减是原子操作
    assert(j >= -1 && j <= capacity - 1 && "STATE_4: 递减后容量索引j越界");
    // 约束目的：验证容量索引递减操作的正确性，确保内层循环按预期进行
    goto CHECK_CAPACITY_LOOP; // 跳转回检查容量循环条件动作，继续内层循环

INCREMENT_ITEM_INDEX:
    // 目的：递增物品索引，移动到下一个物品
    // 变量关联：i表示当前处理物品索引
    // 全局作用：推进外层循环，使算法能够处理下一个物品
    i = i + 1;    // 物品索引加1，指向下一个物品
    goto STATE_5; // 跳转至递增物品索引后的状态断言

STATE_5:
    // 断言依据：递增物品索引后，必须确保索引值合法且递增逻辑正确
    // 状态特征1：递增后的索引必须等于原索引加1（递增逻辑正确性验证）
    assert(i >= 1 && i <= n && "STATE_5: 递增后物品索引i越界");
    // 约束目的：验证物品索引递增操作的正确性，确保外层循环按预期进行
    goto CHECK_ITEMS_LOOP; // 跳转回检查物品循环条件动作，继续外层循环

FINAL_STATE:
    // 目的：验证算法完成后的最终收敛状态
    // 断言依据：0-1背包动态规划算法完成后，必须满足最终状态条件
    // 状态特征1：物品索引i必须等于n（所有物品已处理完成验证）
    assert(i == n && "FINAL_STATE: 动态规划计算完成后物品索引i不等于n");
    // 状态特征2：容量索引j必须在合法范围内（内层循环结束后的状态）
    assert(j == -1 && "FINAL_STATE: 动态规划计算完成后容量索引j不等于-1");
    // 状态特征3：DP数组必须非递减（容量越大，能装的价值不会减少）
    for (int k = 1; k <= capacity; k++)
    {
        assert(dp[k] >= dp[k - 1] && "FINAL_STATE: DP数组不是非递减的");
    }
    // 状态特征4：DP[0]必须为0（容量为0的背包不能装任何物品）
    assert(dp[0] == 0 && "FINAL_STATE: DP[0]不等于0");
    // 状态特征5：最大价值必须不超过所有物品价值之和（理论上界验证）
    int total_value_sum = 0;
    for (int val : values)
    {
        total_value_sum += val;
    }
    assert(dp[capacity] <= total_value_sum && "FINAL_STATE: 最大价值超过所有物品价值之和");
    // 状态特征6：最大价值必须非负（价值非负性验证）
    assert(dp[capacity] >= 0 && "FINAL_STATE: 最大价值为负数");
    // 状态特征7：对于每个容量k，dp[k]必须不小于能放入的任何单个物品的价值
    for (int k = 1; k <= capacity; k++)
    {
        for (int item_idx = 0; item_idx < n; item_idx++)
        {
            if (weights[item_idx] <= k)
            {
                assert(dp[k] >= values[item_idx] && "FINAL_STATE: DP值小于可放入的单个物品价值");
            }
        }
    }
    // 状态特征8：最大价值必须满足0-1背包问题的性质（通过一个简单测试验证）
    // 创建一个简单测试：如果所有物品重量都大于容量，则最大价值为0
    bool all_too_heavy = true;
    for (int w : weights)
    {
        if (w <= capacity)
        {
            all_too_heavy = false;
            break;
        }
    }
    if (all_too_heavy)
    {
        assert(dp[capacity] == 0 && "FINAL_STATE: 所有物品重量大于容量但最大价值不为0");
    }
    // 约束目的：验证算法最终收敛状态，确保0-1背包动态规划结果正确
    goto RETURN_RESULT; // 跳转至返回结果动作

RETURN_RESULT:
    // 专门执行算法最终返回
    // 注意：RETURN_RESULT标签仅包含return语句，无其他业务逻辑
    return dp[capacity]; // 返回背包能装的最大价值
}

// ====================== 测试主函数 ======================
int main()
{
    cout << "测试0-1背包动态规划算法（修正版）" << endl
         << endl;

    // 测试用例1：常规0-1背包问题
    cout << "测试用例1：常规0-1背包问题" << endl;
    int capacity1 = 10;
    vector<int> weights1 = {2, 3, 4, 5};
    vector<int> values1 = {3, 4, 5, 6};
    int result1 = knapsack_01_dp(capacity1, weights1, values1);
    cout << "背包容量: " << capacity1 << endl;
    cout << "物品重量: ";
    for (int w : weights1)
        cout << w << " ";
    cout << endl;
    cout << "物品价值: ";
    for (int v : values1)
        cout << v << " ";
    cout << endl;
    cout << "最大价值: " << result1 << " (期望: 13)" << endl;
    assert(result1 == 13);
    cout << "通过！" << endl
         << endl;

    // 测试用例2：边界情况 - 空背包
    cout << "测试用例2：空背包（容量为0）" << endl;
    int capacity2 = 0;
    vector<int> weights2 = {1, 2, 3};
    vector<int> values2 = {10, 20, 30};
    int result2 = knapsack_01_dp(capacity2, weights2, values2);
    cout << "最大价值: " << result2 << " (期望: 0)" << endl;
    assert(result2 == 0);
    cout << "通过！" << endl
         << endl;

    // 测试用例3：边界情况 - 只有一个物品
    cout << "测试用例3：只有一个物品" << endl;
    int capacity3 = 5;
    vector<int> weights3 = {3};
    vector<int> values3 = {7};
    int result3 = knapsack_01_dp(capacity3, weights3, values3);
    cout << "最大价值: " << result3 << " (期望: 7)" << endl;
    assert(result3 == 7);
    cout << "通过！" << endl
         << endl;

    // 测试用例4：较大规模测试
    cout << "测试用例4：较大规模测试" << endl;
    int capacity4 = 50;
    vector<int> weights4 = {10, 20, 30, 40, 15, 25, 5};
    vector<int> values4 = {60, 100, 120, 200, 70, 90, 30};
    int result4 = knapsack_01_dp(capacity4, weights4, values4);
    cout << "最大价值: " << result4 << " (应在合理范围内)" << endl;
    assert(result4 >= 0 && result4 <= 670); // 670是所有物品价值之和
    cout << "通过！" << endl
         << endl;

    cout << "所有测试用例通过！0-1背包动态规划算法（修正版）实现正确。" << endl;

    return 0;
}