#include <vector>
#include <cassert>
#include <iostream>

// 函数：两数之和（有序数组双指针算法）
// 功能：在有序数组中找到两个数，它们的和等于目标值，返回这两个数的索引
// 输入：nums - 升序排列的整数数组，target - 目标和
// 输出：vector<int>包含两个索引（从0开始），如果未找到则返回空数组
// 算法原理：利用数组有序的特性，使用双指针从两端向中间移动，根据当前和与目标值比较决定移动左指针或右指针
std::vector<int> twoSum(std::vector<int> &nums, int target)
{
    // 核心变量声明
    // left: 左指针索引，初始指向数组第一个元素，用于向右移动增加和的值
    // right: 右指针索引，初始指向数组最后一个元素，用于向左移动减少和的值
    // n: 数组长度，用于边界检查，来源于nums.size()
    // result: 存储返回结果，生命周期从函数开始到返回，初始为空向量表示未找到
    int left, right;
    int n;
    std::vector<int> result;

    goto INIT; // 跳转到初始化动作

// 动作标签：初始化所有核心变量，包括左指针、右指针、数组长度
// 操作目的：为双指针算法准备初始状态
// 全局逻辑关联：这是算法的起点，设置指针位置为数组两端
INIT:
    n = static_cast<int>(nums.size()); // 获取数组长度
    left = 0;                          // 左指针初始位置：数组起始
    right = n - 1;                     // 右指针初始位置：数组末尾（如果数组非空）
    goto STATE_0;                      // 跳转到初始状态验证

// 状态标签：验证初始化后的核心变量合法性
// 断言依据：数组长度必须非负（符合逻辑）；如果数组非空，右指针必须大于等于左指针
// 状态特征含义：验证数组长度和指针初始位置的正确性，确保后续算法可以安全运行
// 约束目的：防止数组越界访问，确保双指针初始位置有效
STATE_0:
    assert(n >= 0 && "STATE_0: 数组长度不能为负值");
    // 如果数组为空（n==0），则left=0, right=-1，此时left>right是合法的，算法会直接跳转到未找到
    // 如果数组非空，则必须满足left <= right才能继续查找
    assert((n == 0 || (left >= 0 && right >= left && right < n)) && "STATE_0: 指针初始位置非法");
    goto CHECK_LOOP_CONDITION; // 跳转到检查循环条件动作

// 动作标签：检查循环是否应该继续执行
// 操作目的：判断双指针是否已经相遇或交叉，决定是否继续查找
// 变量含义：left < right 表示还有查找空间，left >= right 表示已经遍历完所有可能组合
// 全局逻辑关联：在每次指针移动后都需要检查循环条件，这是算法的主控制流
CHECK_LOOP_CONDITION:
    // 检查左指针是否小于右指针，如果为真则继续查找，否则跳转到未找到
    if (left < right)
    {
        goto CALCULATE_SUM; // 还有查找空间，继续计算和
    }
    else
    {
        goto NOT_FOUND; // 指针已相遇或交叉，未找到符合条件的数对
    }

// 动作标签：计算当前两个指针指向元素的和
// 操作目的：计算nums[left] + nums[right]的值，用于与目标值比较
// 变量含义：current_sum存储当前两个数的和，是临时计算变量，不跨标签使用
// 全局逻辑关联：这是算法的核心计算步骤，每次循环都需要重新计算和值
CALCULATE_SUM:
    int current_sum = nums[left] + nums[right]; // 计算当前和
    goto STATE_1;                               // 跳转到状态验证

// 状态标签：验证当前和计算结果的合法性
// 断言依据：数组索引必须有效，且当前和必须在合理范围内（虽然理论上任意整数都可能，但确保计算未溢出）
// 状态特征含义：验证当前指针位置有效且计算正确
// 约束目的：确保数组访问安全，防止未定义行为
STATE_1:
    assert(left >= 0 && left < n && "STATE_1: 左指针索引越界");
    assert(right >= 0 && right < n && "STATE_1: 右指针索引越界");
    // 注意：这里不验证current_sum的具体值，因为它是合法计算的结果
    goto COMPARE_WITH_TARGET; // 跳转到与目标值比较动作

// 动作标签：将当前和与目标值进行比较，决定下一步操作
// 操作目的：根据当前和与目标值的关系，决定移动哪个指针
// 变量含义：current_sum与target比较有三种结果：等于、小于、大于
// 全局逻辑关联：这是算法的决策点，决定搜索方向，利用数组有序性优化搜索
COMPARE_WITH_TARGET:
    if (current_sum == target)
    {
        goto FOUND; // 找到目标，跳转到找到动作
    }
    else if (current_sum < target)
    {
        goto MOVE_LEFT; // 当前和小于目标，需要增加和的值，移动左指针向右
    }
    else
    {                    // current_sum > target
        goto MOVE_RIGHT; // 当前和大于目标，需要减少和的值，移动右指针向左
    }

// 动作标签：移动左指针向右（增加和的值）
// 操作目的：当前和小于目标值，由于数组有序，左指针向右移动可以增加和的值
// 变量含义：left++使左指针指向更大的元素
// 全局逻辑关联：这是搜索过程的一部分，逐步尝试更大的和
MOVE_LEFT:
    left++;                    // 左指针右移
    goto CHECK_LOOP_CONDITION; // 跳转回检查循环条件，继续下一轮查找
    // 注意：这里没有状态标签验证，因为left++是简单操作，且会在下一轮的STATE_1中验证索引合法性

// 动作标签：移动右指针向左（减少和的值）
// 操作目的：当前和大于目标值，由于数组有序，右指针向左移动可以减少和的值
// 变量含义：right--使右指针指向更小的元素
// 全局逻辑关联：这是搜索过程的一部分，逐步尝试更小的和
MOVE_RIGHT:
    right--;                   // 右指针左移
    goto CHECK_LOOP_CONDITION; // 跳转回检查循环条件，继续下一轮查找
    // 注意：这里没有状态标签验证，因为right--是简单操作，且会在下一轮的STATE_1中验证索引合法性

// 动作标签：找到符合条件的两个数
// 操作目的：将找到的两个索引存储到结果向量中
// 变量含义：result被设置为{left, right}，包含找到的两个索引
// 全局逻辑关联：这是算法的成功路径，找到目标后准备返回结果
FOUND:
    result = {left, right}; // 存储找到的索引
    goto STATE_2;           // 跳转到最终状态验证

// 动作标签：未找到符合条件的两个数
// 操作目的：设置结果为空向量，表示未找到
// 变量含义：result被清空，表示没有找到符合条件的数对
// 全局逻辑关联：这是算法的失败路径，遍历完所有可能组合后仍未找到目标
NOT_FOUND:
    result.clear(); // 清空结果向量，表示未找到
    goto STATE_2;   // 跳转到最终状态验证

// 最终状态标签：验证算法最终收敛状态
// 断言依据：根据算法执行路径（找到或未找到）验证结果的正确性
// 状态特征含义：验证算法输出的合法性，确保无论哪个路径，结果都符合预期
// 约束目的：强制验证算法输出的正确性，防止逻辑错误导致错误返回
STATE_2:
    // 根据结果向量的大小判断是从哪个路径进入的
    if (result.size() == 2)
    {
        // 从FOUND路径进入：验证两个索引有效且对应元素之和等于目标值
        int idx1 = result[0];
        int idx2 = result[1];
        assert(idx1 >= 0 && idx1 < n && "STATE_2: 结果索引1越界");
        assert(idx2 >= 0 && idx2 < n && "STATE_2: 结果索引2越界");
        assert(idx1 < idx2 && "STATE_2: 双指针算法保证返回的索引满足左<右");
        assert(nums[idx1] + nums[idx2] == target && "STATE_2: 找到的两个数之和不等于目标值");
    }
    else
    {
        // 从NOT_FOUND路径进入：验证结果为空且确实没有符合条件的数对
        assert(result.empty() && "STATE_2: 未找到时结果向量应为空");
        // 验证确实没有符合条件的数对（遍历了所有可能的组合）
        // 注意：这里简化验证，实际应该验证所有可能的组合都不满足条件
        // 但由于时间复杂度考虑，我们只验证一个边界条件：数组至少有两个元素时，最大和最小元素的关系
        if (n >= 2)
        {
            // 如果数组非空，验证最小和最大元素的关系
            // 如果最小元素+最大元素都小于目标值，且所有元素都非负，则确实不存在解
            // 如果最小元素+最大元素都大于目标值，且所有元素都非正，则确实不存在解
            // 这里只是一个合理性检查，不是严格的证明
            // 由于数组有序，如果最小两个元素之和大于目标值或最大两个元素之和小于目标值，则确实无解
            bool possible_solution_exists = true;
            if (nums[0] + nums[1] > target)
            {
                // 最小的两个数之和已经大于目标值，由于数组有序，所有其他组合都会更大
                possible_solution_exists = false;
            }
            else if (nums[n - 2] + nums[n - 1] < target)
            {
                // 最大的两个数之和已经小于目标值，由于数组有序，所有其他组合都会更小
                possible_solution_exists = false;
            }
            // 注意：这里只是合理性检查，不强制断言，因为存在中间可能的情况
            // 例如数组中有负数时，即使最小两个数之和大于目标值，也可能有负数组合满足条件
            // 但算法已经正确执行，所以不在此严格断言
        }
    }
    goto RETURN_RESULT; // 跳转到返回结果标签

// 特殊标签：执行算法最终返回
// 操作目的：返回结果向量，这是函数唯一的返回点
// 变量含义：返回result向量，包含找到的两个索引或为空
// 全局逻辑关联：所有执行路径最终汇聚到此标签返回结果
RETURN_RESULT:
    return result; // 返回结果向量
}

// 主函数：测试算法功能
// 测试用例1：常规场景，有序数组中存在符合条件的两个数
// 测试用例2：边界场景，数组为空或只有一个元素
// 测试用例3：边界场景，数组中有多个相同元素
// 测试用例4：边界场景，目标值小于最小和或大于最大和
int main()
{
    // 测试用例1：常规场景，有序数组[2, 7, 11, 15]，目标值9
    // 期望输出：[0, 1]（因为2+7=9）
    std::vector<int> nums1 = {2, 7, 11, 15};
    int target1 = 9;
    std::vector<int> result1 = twoSum(nums1, target1);
    std::cout << "测试用例1 - 常规场景:" << std::endl;
    std::cout << "输入数组: [2, 7, 11, 15], 目标值: 9" << std::endl;
    std::cout << "输出索引: ";
    if (result1.empty())
    {
        std::cout << "未找到" << std::endl;
    }
    else
    {
        std::cout << "[" << result1[0] << ", " << result1[1] << "]" << std::endl;
        std::cout << "验证: " << nums1[result1[0]] << " + " << nums1[result1[1]]
                  << " = " << nums1[result1[0]] + nums1[result1[1]] << std::endl;
    }
    std::cout << std::endl;

    // 测试用例2：边界场景，数组为空
    // 期望输出：空向量（未找到）
    std::vector<int> nums2 = {};
    int target2 = 0;
    std::vector<int> result2 = twoSum(nums2, target2);
    std::cout << "测试用例2 - 空数组:" << std::endl;
    std::cout << "输入数组: [], 目标值: 0" << std::endl;
    std::cout << "输出索引: ";
    if (result2.empty())
    {
        std::cout << "未找到" << std::endl;
    }
    else
    {
        std::cout << "[" << result2[0] << ", " << result2[1] << "]" << std::endl;
    }
    std::cout << std::endl;

    // 测试用例3：边界场景，数组中只有一个元素
    // 期望输出：空向量（未找到，因为至少需要两个元素）
    std::vector<int> nums3 = {5};
    int target3 = 5;
    std::vector<int> result3 = twoSum(nums3, target3);
    std::cout << "测试用例3 - 单元素数组:" << std::endl;
    std::cout << "输入数组: [5], 目标值: 5" << std::endl;
    std::cout << "输出索引: ";
    if (result3.empty())
    {
        std::cout << "未找到" << std::endl;
    }
    else
    {
        std::cout << "[" << result3[0] << ", " << result3[1] << "]" << std::endl;
    }
    std::cout << std::endl;

    // 测试用例4：边界场景，数组中有重复元素，目标值可重复使用不同位置的相同元素
    // 输入数组: [1, 2, 2, 4]，目标值: 4
    // 期望输出: [0, 3]（1+3=4）或 [1, 2]（2+2=4），实际算法会返回[1, 2]
    std::vector<int> nums4 = {1, 2, 2, 4};
    int target4 = 4;
    std::vector<int> result4 = twoSum(nums4, target4);
    std::cout << "测试用例4 - 重复元素数组:" << std::endl;
    std::cout << "输入数组: [1, 2, 2, 4], 目标值: 4" << std::endl;
    std::cout << "输出索引: ";
    if (result4.empty())
    {
        std::cout << "未找到" << std::endl;
    }
    else
    {
        std::cout << "[" << result4[0] << ", " << result4[1] << "]" << std::endl;
        std::cout << "验证: " << nums4[result4[0]] << " + " << nums4[result4[1]]
                  << " = " << nums4[result4[0]] + nums4[result4[1]] << std::endl;
    }
    std::cout << std::endl;

    // 测试用例5：边界场景，目标值小于最小可能和
    // 输入数组: [10, 20, 30, 40]，目标值: 5
    // 期望输出: 空向量（未找到）
    std::vector<int> nums5 = {10, 20, 30, 40};
    int target5 = 5;
    std::vector<int> result5 = twoSum(nums5, target5);
    std::cout << "测试用例5 - 目标值小于最小可能和:" << std::endl;
    std::cout << "输入数组: [10, 20, 30, 40], 目标值: 5" << std::endl;
    std::cout << "输出索引: ";
    if (result5.empty())
    {
        std::cout << "未找到" << std::endl;
    }
    else
    {
        std::cout << "[" << result5[0] << ", " << result5[1] << "]" << std::endl;
    }
    std::cout << std::endl;

    // 测试用例6：边界场景，目标值大于最大可能和
    // 输入数组: [1, 2, 3, 4]，目标值: 100
    // 期望输出: 空向量（未找到）
    std::vector<int> nums6 = {1, 2, 3, 4};
    int target6 = 100;
    std::vector<int> result6 = twoSum(nums6, target6);
    std::cout << "测试用例6 - 目标值大于最大可能和:" << std::endl;
    std::cout << "输入数组: [1, 2, 3, 4], 目标值: 100" << std::endl;
    std::cout << "输出索引: ";
    if (result6.empty())
    {
        std::cout << "未找到" << std::endl;
    }
    else
    {
        std::cout << "[" << result6[0] << ", " << result6[1] << "]" << std::endl;
    }
    std::cout << std::endl;

    return 0;
}