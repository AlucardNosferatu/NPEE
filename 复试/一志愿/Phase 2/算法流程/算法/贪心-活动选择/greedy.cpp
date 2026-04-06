#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

// 函数：activity_selection_goto
// 功能：基于贪心算法求解最大兼容活动子集
// 输入：activities - 活动列表，每个活动是pair<开始时间, 结束时间>
// 输出：选中的活动索引列表（按结束时间排序后的原索引顺序）
std::vector<int> activity_selection_goto(const std::vector<std::pair<int, int>> &activities)
{
    // 核心变量声明区域
    // sorted_activities: 存储带原索引的排序后活动，用于按结束时间排序并保留原索引
    // selected_indices: 存储最终选中的活动原索引
    // last_selected_end: 记录上一个选中活动的结束时间，用于判断兼容性
    // n: 活动总数，用于循环控制
    // i: 循环索引，用于遍历排序后的活动
    std::vector<std::pair<std::pair<int, int>, int>> sorted_activities;
    std::vector<int> selected_indices;
    int last_selected_end = 0;
    int n = 0;
    int i = 0;

    // 动作标签：INIT - 初始化数据结构，准备活动数据
    // 操作目的：复制输入活动并添加原索引，为排序做准备
    // 变量含义：sorted_activities存储(活动时间, 原索引)对，便于排序后跟踪原位置
    // 全局逻辑关联：这是算法起点，为后续排序和选择建立数据结构基础
INIT:
    n = static_cast<int>(activities.size());

    // 为每个活动添加原索引，创建可排序的数据结构
    for (int idx = 0; idx < n; ++idx)
    {
        sorted_activities.push_back(std::make_pair(activities[idx], idx));
    }

    // 根据活动数量决定下一步操作
    if (n == 0)
    {
        // 空活动列表，直接跳转到最终状态
        goto FINAL_STATE;
    }
    else
    {
        // 非空活动列表，跳转到非空状态验证
        goto STATE_0;
    }

    // 状态标签：STATE_0 - 验证非空活动列表初始化状态
    // 断言依据：活动数量n应大于0，sorted_activities大小应与n一致
    // 状态特征含义：确认活动列表非空，可以进行后续排序操作
    // 约束目的：确保非空输入情况下数据结构的正确初始化
STATE_0:
    assert(n > 0 && "STATE_0: 非空活动列表情况下n应大于0");
    assert(static_cast<int>(sorted_activities.size()) == n &&
           "STATE_0: sorted_activities大小应与活动数量n一致");
    goto SORT_ACTIVITIES;

    // 动作标签：SORT_ACTIVITIES - 按结束时间对活动进行排序
    // 操作目的：按照贪心策略要求，将活动按结束时间升序排列
    // 变量含义：sorted_activities排序后，最早结束的活动在前，便于贪心选择
    // 全局逻辑关联：这是贪心算法的核心预处理步骤，确保后续选择最优
SORT_ACTIVITIES:
    std::sort(sorted_activities.begin(), sorted_activities.end(),
              [](const std::pair<std::pair<int, int>, int> &a,
                 const std::pair<std::pair<int, int>, int> &b)
              {
                  // 按结束时间排序，结束时间相同则按开始时间排序
                  if (a.first.second != b.first.second)
                  {
                      return a.first.second < b.first.second;
                  }
                  return a.first.first < b.first.first;
              });

    goto STATE_1;

    // 状态标签：STATE_1 - 验证活动排序后的状态
    // 断言依据：排序后活动应按结束时间升序排列，结束时间相同的按开始时间升序
    // 状态特征含义：确认活动已正确排序，符合贪心算法的预处理要求
    // 约束目的：确保排序操作正确执行，为后续贪心选择提供正确的顺序
STATE_1:
    // 验证排序后的活动按结束时间升序排列
    for (int idx = 1; idx < n; ++idx)
    {
        assert(sorted_activities[idx].first.second >= sorted_activities[idx - 1].first.second &&
               "STATE_1: 活动应按结束时间升序排列");
        // 如果结束时间相同，验证开始时间也按升序排列
        if (sorted_activities[idx].first.second == sorted_activities[idx - 1].first.second)
        {
            assert(sorted_activities[idx].first.first >= sorted_activities[idx - 1].first.first &&
                   "STATE_1: 结束时间相同时，活动应按开始时间升序排列");
        }
    }

    // 验证sorted_activities大小不变
    assert(static_cast<int>(sorted_activities.size()) == n &&
           "STATE_1: 排序后活动数量应保持不变");

    goto SELECT_FIRST_ACTIVITY;

    // 动作标签：SELECT_FIRST_ACTIVITY - 选择第一个活动（结束时间最早）
    // 操作目的：按照贪心策略，总是选择第一个可用的活动（结束时间最早）
    // 变量含义：last_selected_end更新为第一个活动的结束时间，为后续兼容性检查提供基准
    // 全局逻辑关联：这是贪心选择的起点，建立初始选中活动
SELECT_FIRST_ACTIVITY:
    // 总是选择第一个活动（按结束时间排序后）
    selected_indices.push_back(sorted_activities[0].second);
    last_selected_end = sorted_activities[0].first.second;
    i = 1; // 从第二个活动开始检查

    goto STATE_2;

    // 状态标签：STATE_2 - 验证第一个活动选择后的状态
    // 断言依据：selected_indices应包含一个索引，last_selected_end应为第一个活动的结束时间
    // 状态特征含义：确认贪心算法的初始选择已正确执行
    // 约束目的：确保算法从正确状态开始后续遍历
STATE_2:
    assert(!selected_indices.empty() && "STATE_2: 第一个活动必须被选中");
    assert(selected_indices[0] == sorted_activities[0].second &&
           "STATE_2: 选中的应是排序后的第一个活动的原索引");
    assert(last_selected_end == sorted_activities[0].first.second &&
           "STATE_2: last_selected_end应等于第一个活动的结束时间");
    assert(i == 1 && "STATE_2: 循环索引i应初始化为1");
    goto CHECK_NEXT_ACTIVITY;

    // 动作标签：CHECK_NEXT_ACTIVITY - 检查下一个活动是否兼容
    // 操作目的：遍历剩余活动，选择第一个与已选活动兼容的活动
    // 变量含义：i为当前检查的活动索引，last_selected_end为上一个选中活动的结束时间
    // 全局逻辑关联：这是贪心算法的核心循环，实现"选择最早结束的兼容活动"策略
CHECK_NEXT_ACTIVITY:
    // 遍历剩余活动，选择兼容活动
    if (i < n)
    {
        // 检查当前活动是否与上一个选中活动兼容（开始时间 >= 上一个活动的结束时间）
        if (sorted_activities[i].first.first >= last_selected_end)
        {
            // 活动兼容，跳转到兼容状态标签
            goto STATE_3;
        }
        else
        {
            // 活动不兼容，跳转到不兼容状态标签
            goto STATE_4;
        }
    }
    else
    {
        // 所有活动检查完毕，跳转到最终状态
        goto FINAL_STATE;
    }

    // 状态标签：STATE_3 - 验证当前活动兼容状态
    // 断言依据：当前活动的开始时间应大于等于上一个选中活动的结束时间
    // 状态特征含义：确认当前活动满足兼容性条件，可以被选中
    // 约束目的：确保只有兼容的活动才会被选中
STATE_3:
    assert(i < n && "STATE_3: 当前索引i应在有效范围内");
    assert(sorted_activities[i].first.first >= last_selected_end &&
           "STATE_3: 当前活动的开始时间应大于等于上一个选中活动的结束时间");
    goto SELECT_COMPATIBLE_ACTIVITY;

    // 状态标签：STATE_4 - 验证当前活动不兼容状态
    // 断言依据：当前活动的开始时间应小于上一个选中活动的结束时间
    // 状态特征含义：确认当前活动不满足兼容性条件，需要跳过
    // 约束目的：确保不兼容的活动不会被选中
STATE_4:
    assert(i < n && "STATE_4: 当前索引i应在有效范围内");
    assert(sorted_activities[i].first.first < last_selected_end &&
           "STATE_4: 当前活动的开始时间应小于上一个选中活动的结束时间");
    goto SKIP_INCOMPATIBLE_ACTIVITY;

    // 动作标签：SELECT_COMPATIBLE_ACTIVITY - 选择兼容的活动
    // 操作目的：将兼容的活动加入选中列表，更新上一个选中活动的结束时间
    // 变量含义：将当前活动原索引加入selected_indices，更新last_selected_end为当前活动结束时间
    // 全局逻辑关联：这是贪心选择的具体实现，每次选择都保证局部最优
SELECT_COMPATIBLE_ACTIVITY:
    selected_indices.push_back(sorted_activities[i].second);
    last_selected_end = sorted_activities[i].first.second;
    i++; // 移动到下一个活动

    goto STATE_5;

    // 动作标签：SKIP_INCOMPATIBLE_ACTIVITY - 跳过不兼容的活动
    // 操作目的：跳过不兼容的活动，继续检查下一个活动
    // 变量含义：i递增，跳过当前不兼容的活动
    // 全局逻辑关联：这是贪心算法的关键步骤，跳过不兼容的活动以寻找下一个兼容活动
SKIP_INCOMPATIBLE_ACTIVITY:
    i++; // 跳过当前不兼容的活动

    goto STATE_6;

    // 状态标签：STATE_5 - 验证选择兼容活动后的状态
    // 断言依据：selected_indices应包含新选中的活动，last_selected_end应更新，i应递增
    // 状态特征含义：确认兼容活动已被正确选中，状态已更新
    // 约束目的：确保选择操作正确执行，为后续检查做好准备
STATE_5:
    // 验证选中活动列表不为空
    assert(!selected_indices.empty() && "STATE_5: 选中活动列表不应为空");

    // 验证最后一个选中的活动与上一个选中活动兼容（如果存在上一个）
    if (selected_indices.size() > 1)
    {
        int last_idx = selected_indices.back();
        // 查找最后一个选中活动在sorted_activities中的位置
        int sorted_pos = 0;
        for (int k = 0; k < n; ++k)
        {
            if (sorted_activities[k].second == last_idx)
            {
                sorted_pos = k;
                break;
            }
        }
        // 验证兼容性：当前活动的开始时间应 >= 上一个选中活动的结束时间
        // 注意：由于按结束时间排序，我们只需要检查与上一个选中活动的兼容性
        int prev_sorted_pos = 0;
        for (int k = 0; k < n; ++k)
        {
            if (sorted_activities[k].second == selected_indices[selected_indices.size() - 2])
            {
                prev_sorted_pos = k;
                break;
            }
        }
        assert(sorted_activities[sorted_pos].first.first >= sorted_activities[prev_sorted_pos].first.second &&
               "STATE_5: 选中活动必须与上一个选中活动兼容");
    }

    // 验证i已正确递增（指向下一个待检查活动）
    assert(i > 0 && i <= n && "STATE_5: 索引i应在有效范围内");

    goto CHECK_NEXT_ACTIVITY;

    // 状态标签：STATE_6 - 验证跳过不兼容活动后的状态
    // 断言依据：i应递增，但选中活动列表和last_selected_end不应改变
    // 状态特征含义：确认不兼容活动已被正确跳过，状态未受影响
    // 约束目的：确保跳过操作正确执行，为后续检查做好准备
STATE_6:
    // 验证i已正确递增（指向下一个待检查活动）
    assert(i > 0 && i <= n && "STATE_6: 索引i应在有效范围内");

    // 验证last_selected_end未改变（跳过不兼容活动不应影响上一个选中活动的结束时间）
    if (!selected_indices.empty())
    {
        int last_selected_idx = selected_indices.back();
        // 查找最后一个选中活动在sorted_activities中的位置
        int sorted_pos = 0;
        for (int k = 0; k < n; ++k)
        {
            if (sorted_activities[k].second == last_selected_idx)
            {
                sorted_pos = k;
                break;
            }
        }
        assert(last_selected_end == sorted_activities[sorted_pos].first.second &&
               "STATE_6: last_selected_end应与最后一个选中活动的结束时间一致");
    }

    goto CHECK_NEXT_ACTIVITY;

    // 状态标签：FINAL_STATE - 最终状态验证
    // 断言依据：验证最终选中的活动集合满足最大兼容性和算法正确性
    // 状态特征含义：确认算法输出是有效的最大兼容活动子集
    // 约束目的：确保算法结果符合贪心策略的预期
    // 注意：此状态标签合并了空列表和非空列表两种情况的验证，通过条件判断区分
FINAL_STATE:
    // 情况1：空活动列表验证（来自INIT的直接跳转）
    if (n == 0)
    {
        assert(sorted_activities.empty() && "FINAL_STATE: 空活动列表情况下sorted_activities应为空");
        assert(selected_indices.empty() && "FINAL_STATE: 空活动列表情况下selected_indices应为空");
        goto RETURN_RESULT;
    }

    // 情况2：非空活动列表验证（来自CHECK_NEXT_ACTIVITY的跳转）
    // 验证选中的活动数量不超过总活动数
    assert(selected_indices.size() <= static_cast<size_t>(n) &&
           "FINAL_STATE: 选中活动数量不能超过总活动数");

    // 验证选中活动集合内部兼容（无时间冲突）
    if (!selected_indices.empty())
    {
        // 将选中活动按原索引查找其时间信息
        std::vector<std::pair<int, int>> selected_activities;
        for (int idx : selected_indices)
        {
            // 在原始活动中查找
            for (size_t k = 0; k < activities.size(); ++k)
            {
                if (static_cast<int>(k) == idx)
                {
                    selected_activities.push_back(activities[k]);
                    break;
                }
            }
        }

        // 验证选中活动按结束时间排序（贪心选择的结果）
        for (size_t k = 1; k < selected_activities.size(); ++k)
        {
            assert(selected_activities[k].first >= selected_activities[k - 1].second &&
                   "FINAL_STATE: 选中活动必须按时间顺序且兼容");
        }

        // 验证选中活动是最大兼容子集（贪心特性）
        // 注意：这里不验证全局最优，因为贪心算法对于活动选择问题是全局最优的
        // 我们验证选中活动数量至少为1（除非输入为空）
        assert(!selected_indices.empty() &&
               "FINAL_STATE: 非空输入至少应选中一个活动");
    }

    // 验证所有活动都已检查完毕
    assert(i == n && "FINAL_STATE: 所有活动都应被检查");

    goto RETURN_RESULT;

    // 特殊标签：RETURN_RESULT - 执行最终返回
    // 操作目的：返回算法结果，不包含任何业务逻辑
    // 变量含义：selected_indices包含所有选中活动的原索引
    // 全局逻辑关联：这是算法的终点，返回最终计算结果
RETURN_RESULT:
    return selected_indices;
}

// 主函数：测试活动选择算法
int main()
{
    std::cout << "=== 活动选择问题测试 ===\n"
              << std::endl;

    // 测试用例1：常规场景 - 多个活动
    // 测试目的：验证算法在常规情况下的正确性和贪心策略
    {
        std::vector<std::pair<int, int>> activities = {
            {1, 4}, {3, 5}, {0, 6}, {5, 7}, {3, 9}, {5, 9}, {6, 10}, {8, 11}, {8, 12}, {2, 14}, {12, 16}};

        std::cout << "测试用例1 - 常规场景：" << std::endl;
        std::cout << "活动列表（开始时间, 结束时间）：";
        for (size_t i = 0; i < activities.size(); ++i)
        {
            std::cout << "(" << activities[i].first << "," << activities[i].second << ") ";
            if (i > 0 && i % 5 == 0)
                std::cout << std::endl
                          << "                    ";
        }
        std::cout << std::endl;

        std::vector<int> result = activity_selection_goto(activities);

        std::cout << "选中活动原索引：";
        for (int idx : result)
        {
            std::cout << idx << " ";
        }
        std::cout << std::endl;

        std::cout << "选中活动详情：" << std::endl;
        for (int idx : result)
        {
            std::cout << "  活动" << idx << ": (" << activities[idx].first
                      << ", " << activities[idx].second << ")" << std::endl;
        }
        std::cout << "选中活动数量：" << result.size() << std::endl;

        // 验证选中活动兼容性
        bool compatible = true;
        int last_end = -1;
        for (int idx : result)
        {
            if (last_end != -1 && activities[idx].first < last_end)
            {
                compatible = false;
                break;
            }
            last_end = activities[idx].second;
        }
        std::cout << "兼容性验证：" << (compatible ? "通过" : "失败") << std::endl;
        std::cout << std::endl;
    }

    // 测试用例2：边界场景 - 单个活动
    // 测试目的：验证算法在最小输入情况下的正确处理
    {
        std::vector<std::pair<int, int>> activities = {{2, 5}};

        std::cout << "测试用例2 - 单个活动：" << std::endl;
        std::cout << "活动列表（开始时间, 结束时间）：";
        std::cout << "(" << activities[0].first << "," << activities[0].second << ")" << std::endl;

        std::vector<int> result = activity_selection_goto(activities);

        std::cout << "选中活动原索引：";
        for (int idx : result)
        {
            std::cout << idx << " ";
        }
        std::cout << std::endl;

        if (!result.empty())
        {
            std::cout << "选中活动详情：" << std::endl;
            for (int idx : result)
            {
                std::cout << "  活动" << idx << ": (" << activities[idx].first
                          << ", " << activities[idx].second << ")" << std::endl;
            }
        }
        std::cout << "选中活动数量：" << result.size() << std::endl;
        std::cout << std::endl;
    }

    // 测试用例3：边界场景 - 空活动列表
    // 测试目的：验证算法对空输入的处理能力
    {
        std::vector<std::pair<int, int>> activities = {};

        std::cout << "测试用例3 - 空活动列表：" << std::endl;
        std::cout << "活动列表：空" << std::endl;

        std::vector<int> result = activity_selection_goto(activities);

        std::cout << "选中活动原索引：";
        if (result.empty())
        {
            std::cout << "空";
        }
        else
        {
            for (int idx : result)
            {
                std::cout << idx << " ";
            }
        }
        std::cout << std::endl;
        std::cout << "选中活动数量：" << result.size() << std::endl;
        std::cout << std::endl;
    }

    // 测试用例4：特殊场景 - 所有活动互不冲突
    // 测试目的：验证算法在理想情况下的选择能力
    {
        std::vector<std::pair<int, int>> activities = {
            {1, 2}, {2, 3}, {3, 4}, {4, 5}, {5, 6}};

        std::cout << "测试用例4 - 所有活动互不冲突：" << std::endl;
        std::cout << "活动列表（开始时间, 结束时间）：";
        for (size_t i = 0; i < activities.size(); ++i)
        {
            std::cout << "(" << activities[i].first << "," << activities[i].second << ") ";
        }
        std::cout << std::endl;

        std::vector<int> result = activity_selection_goto(activities);

        std::cout << "选中活动原索引：";
        for (int idx : result)
        {
            std::cout << idx << " ";
        }
        std::cout << std::endl;

        std::cout << "选中活动详情：" << std::endl;
        for (int idx : result)
        {
            std::cout << "  活动" << idx << ": (" << activities[idx].first
                      << ", " << activities[idx].second << ")" << std::endl;
        }
        std::cout << "选中活动数量：" << result.size() << std::endl;

        // 验证是否选中了所有活动
        std::cout << "是否选中所有活动：" << (result.size() == activities.size() ? "是" : "否") << std::endl;
        std::cout << std::endl;
    }

    // 测试用例5：特殊场景 - 所有活动时间完全重叠
    // 测试目的：验证算法在极端冲突情况下的选择策略
    {
        std::vector<std::pair<int, int>> activities = {
            {1, 5}, {1, 5}, {1, 5}, {1, 5}};

        std::cout << "测试用例5 - 所有活动时间完全重叠：" << std::endl;
        std::cout << "活动列表（开始时间, 结束时间）：";
        for (size_t i = 0; i < activities.size(); ++i)
        {
            std::cout << "(" << activities[i].first << "," << activities[i].second << ") ";
        }
        std::cout << std::endl;

        std::vector<int> result = activity_selection_goto(activities);

        std::cout << "选中活动原索引：";
        for (int idx : result)
        {
            std::cout << idx << " ";
        }
        std::cout << std::endl;

        if (!result.empty())
        {
            std::cout << "选中活动详情：" << std::endl;
            for (int idx : result)
            {
                std::cout << "  活动" << idx << ": (" << activities[idx].first
                          << ", " << activities[idx].second << ")" << std::endl;
            }
        }
        std::cout << "选中活动数量：" << result.size() << " (预期为1)" << std::endl;
        std::cout << std::endl;
    }

    std::cout << "=== 所有测试完成 ===" << std::endl;

    return 0;
}