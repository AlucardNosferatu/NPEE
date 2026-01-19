#include <iostream>
#include <vector>
#include <cassert>
#include <string>
using namespace std;

// 有序数组二分查找目标值：在有序数组中找到目标值的索引
// 输入参数：nums - 有序整数数组（升序），target - 要查找的目标值
// 输出参数：目标值在数组中的索引（如果找到），否则返回-1
// 核心思想：通过不断将搜索区间减半来快速定位目标值
int binary_search(vector<int> nums, int target)
{
    // ====================== 核心变量声明 ======================
    int left;             // 用途：左边界指针，指向当前搜索区间的左边界；数据来源：初始化为0；生命周期：整个算法执行期间
    int right;            // 用途：右边界指针，指向当前搜索区间的右边界；数据来源：初始化为n-1；生命周期：整个算法执行期间
    int mid;              // 用途：中间指针，指向当前搜索区间的中点；数据来源：计算(left+right)/2；生命周期：单次循环期间
    int n;                // 用途：数组长度；数据来源：nums.size()；生命周期：整个算法执行期间
    bool continue_search; // 用途：控制搜索是否继续的标志；数据来源：比较left和right；生命周期：循环控制期间
    int result_index;     // 用途：存储找到的目标索引（如果找到）；数据来源：找到目标时赋值；生命周期：整个算法执行期间

// ====================== 算法开始 ======================
INIT:
    // 目的：初始化算法所需的核心变量和数据结构
    // 变量关联：left初始为0，right初始为n-1，result_index初始为-1（表示未找到）
    // 全局作用：为二分查找算法准备初始状态，设置搜索区间
    n = static_cast<int>(nums.size()); // 获取数组长度，用于后续边界控制
    // 输入验证：数组必须有序（升序）
    for (int i = 1; i < n; i++)
    {
        assert(nums[i] >= nums[i - 1] && "INIT: 输入数组不是升序");
    }
    left = 0;               // 左边界指向数组第一个元素
    right = n - 1;          // 右边界指向数组最后一个元素
    continue_search = true; // 初始时允许继续搜索
    result_index = -1;      // 初始结果索引为-1（表示未找到）
    mid = 0;                // 初始化中间指针
    goto STATE_0;           // 跳转至初始状态断言：验证变量初始化合法性

STATE_0:
    // 断言依据：初始化后必须确保核心变量处于合法初始状态
    // 状态特征1：左指针必须为0（指向数组开头）
    assert(left == 0 && "STATE_0: 左指针初始状态不是0");
    // 状态特征2：右指针必须为n-1（指向数组末尾，如果数组非空）
    if (n > 0)
    {
        assert(right == n - 1 && "STATE_0: 右指针初始状态不是n-1");
    }
    else
    {
        assert(right == -1 && "STATE_0: 空数组时右指针不是-1");
    }
    // 状态特征3：结果索引必须为-1（初始状态未找到任何元素）
    assert(result_index == -1 && "STATE_0: 结果索引初始状态不是-1");
    // 状态特征4：数组必须有序（在INIT中已经验证，这里不再重复）
    // 约束目的：验证算法初始化的正确性，确保从正确状态开始二分查找
    goto UPDATE_SEARCH_CONDITION; // 跳转至更新搜索条件动作

UPDATE_SEARCH_CONDITION:
    // 目的：更新搜索是否继续的条件
    // 变量关联：left和right定义当前搜索区间，continue_search表示是否继续
    // 全局作用：控制二分查找的主循环，决定是继续搜索还是结束
    // 注意：这是循环控制的关键节点，每次迭代都会更新这个条件
    if (left <= right)
    {                           // 如果左边界不超过右边界，搜索区间有效
        continue_search = true; // 设置继续搜索标志为true
    }
    else
    {
        continue_search = false; // 设置继续搜索标志为false，表示搜索完成
    }
    goto STATE_1; // 跳转至搜索条件更新后的状态断言

STATE_1:
    // 断言依据：搜索条件更新后，搜索标志必须正确反映搜索区间的有效性
    // 状态特征1：搜索标志的值必须与(left <= right)的逻辑结果一致
    assert(continue_search == (left <= right) && "STATE_1: 搜索标志与区间有效性不一致");
    // 状态特征2：左指针必须在合理范围内（0到n之间，包括n表示区间为空）
    assert(left >= 0 && left <= n && "STATE_1: 左指针越界");
    // 状态特征3：右指针必须在合理范围内（-1到n-1之间，包括-1表示区间为空）
    assert(right >= -1 && right < n && "STATE_1: 右指针越界");
    // 状态特征4：如果搜索继续为true，左指针必须小于等于右指针；如果为false，左指针必须大于右指针
    if (continue_search)
    {
        assert(left <= right && "STATE_1: 搜索继续但左指针大于右指针");
    }
    else
    {
        assert(left > right && "STATE_1: 搜索停止但左指针不大于右指针");
    }
    // 约束目的：验证搜索条件更新的正确性，确保搜索控制逻辑一致
    goto CHECK_SEARCH_CONTINUE; // 跳转至检查搜索继续动作

CHECK_SEARCH_CONTINUE:
    // 目的：根据搜索继续标志决定下一步操作
    // 变量关联：continue_search标志控制算法流程
    // 全局作用：实现二分查找的主循环控制，决定是继续搜索还是结束
    // 注意：这是算法的主循环控制点，每次迭代都会执行这个检查
    if (continue_search)
    {                       // 如果搜索需要继续
        goto CALCULATE_MID; // 跳转至计算中点动作
    }
    else
    {
        goto FINAL_STATE; // 跳转至最终状态验证，准备返回结果
    }

CALCULATE_MID:
    // 目的：计算当前搜索区间的中点
    // 变量关联：left和right定义区间，mid是中点
    // 全局作用：实现二分查找的核心步骤，将搜索区间对半分割
    // 注意：使用(left+right)/2可能会溢出，所以使用left+(right-left)/2
    mid = left + (right - left) / 2; // 计算中间索引
    goto STATE_2;                    // 跳转至计算中点后的状态断言

STATE_2:
    // 断言依据：计算中点后，必须确保中点索引有效且计算正确
    // 状态特征1：中点索引必须在当前搜索区间内[left, right]
    assert(mid >= left && mid <= right && "STATE_2: 中点索引不在当前搜索区间内");
    // 状态特征2：中点索引必须在数组有效范围内（0到n-1）
    if (n > 0)
    {
        assert(mid >= 0 && mid < n && "STATE_2: 中点索引越界");
    }
    // 状态特征3：中点索引的计算公式必须正确（二分查找中点计算验证）
    // 检查mid确实等于left+(right-left)/2
    assert(mid == left + (right - left) / 2 && "STATE_2: 中点计算错误");
    // 状态特征4：如果区间长度为奇数，中点应偏向左；如果为偶数，中点应正确计算
    // 约束目的：验证中点计算操作的正确性，确保二分查找的分割点正确
    goto COMPARE_WITH_TARGET; // 跳转至与目标值比较动作

COMPARE_WITH_TARGET:
    // 目的：将中点元素与目标值比较，决定下一步操作
    // 变量关联：mid指向的元素值，target是要查找的目标值
    // 全局作用：根据比较结果决定如何调整搜索区间，这是二分查找的关键决策
    // 注意：二分查找通过比较不断缩小搜索范围
    if (nums[mid] == target)
    {                      // 如果中点元素等于目标值，找到目标
        goto FOUND_RESULT; // 跳转至找到结果动作
    }
    else if (nums[mid] < target)
    {                     // 如果中点元素小于目标值，目标在右半部分
        goto ADJUST_LEFT; // 跳转至调整左边界动作
    }
    else
    {                      // 如果中点元素大于目标值，目标在左半部分
        goto ADJUST_RIGHT; // 跳转至调整右边界动作
    }

ADJUST_LEFT:
    // 目的：调整左边界，搜索右半部分
    // 变量关联：left指针移动到mid+1
    // 全局作用：当中点元素小于目标值时，目标值在右半部分，调整左边界缩小搜索范围
    left = mid + 1; // 左边界移动到中点右侧
    goto STATE_3;   // 跳转至调整左边界后的状态断言

STATE_3:
    // 断言依据：调整左边界后，状态必须正确更新
    // 状态特征1：左指针必须增加（移动到mid+1）
    assert(left == mid + 1 && "STATE_3: 调整左边界后左指针不等于mid+1");
    // 状态特征2：左指针不能超过右指针+1（否则搜索区间无效）
    assert(left <= right + 1 && "STATE_3: 调整左边界后左指针超过右指针+1");
    // 状态特征3：左指针必须在合理范围内（0到n之间）
    assert(left >= 0 && left <= n && "STATE_3: 调整左边界后左指针越界");
    // 状态特征4：调整前的nums[mid]必须小于target（调整条件验证）
    // 注意：这个断言需要记录调整前的nums[mid]，但状态标签中不能有分支
    // 我们可以通过检查调整后的搜索区间特性来间接验证
    // 约束目的：验证调整左边界操作的正确性，确保搜索区间缩小方向正确
    goto UPDATE_SEARCH_CONDITION; // 跳转回更新搜索条件动作，继续搜索

ADJUST_RIGHT:
    // 目的：调整右边界，搜索左半部分
    // 变量关联：right指针移动到mid-1
    // 全局作用：当中点元素大于目标值时，目标值在左半部分，调整右边界缩小搜索范围
    right = mid - 1; // 右边界移动到中点左侧
    goto STATE_4;    // 跳转至调整右边界后的状态断言

STATE_4:
    // 断言依据：调整右边界后，状态必须正确更新
    // 状态特征1：右指针必须减少（移动到mid-1）
    assert(right == mid - 1 && "STATE_4: 调整右边界后右指针不等于mid-1");
    // 状态特征2：右指针不能小于左指针-1（否则搜索区间无效）
    assert(right >= left - 1 && "STATE_4: 调整右边界后右指针小于左指针-1");
    // 状态特征3：右指针必须在合理范围内（-1到n-1之间）
    assert(right >= -1 && right < n && "STATE_4: 调整右边界后右指针越界");
    // 状态特征4：调整前的nums[mid]必须大于target（调整条件验证）
    // 注意：这个断言需要记录调整前的nums[mid]，但状态标签中不能有分支
    // 约束目的：验证调整右边界操作的正确性，确保搜索区间缩小方向正确
    goto UPDATE_SEARCH_CONDITION; // 跳转回更新搜索条件动作，继续搜索

FOUND_RESULT:
    // 目的：找到目标值，记录结果索引
    // 变量关联：mid是找到的目标索引，result_index存储结果
    // 全局作用：记录找到的目标索引，准备返回结果
    result_index = mid; // 将中点索引（找到的目标索引）赋值给结果
    goto FINAL_STATE;   // 直接跳转到最终状态

FINAL_STATE:
    // 目的：验证算法完成后的最终收敛状态并返回结果
    // 断言依据：二分查找算法完成后，必须满足特定最终状态
    // 状态特征1：如果找到目标值，结果索引必须有效且对应元素等于目标值
    if (result_index != -1)
    {
        assert(result_index >= 0 && result_index < n && "FINAL_STATE: 找到结果但结果索引越界");
        assert(nums[result_index] == target && "FINAL_STATE: 找到结果但元素值不等于目标值");
    }
    else
    {
        // 状态特征2：如果未找到目标值，结果索引必须为-1
        assert(result_index == -1 && "FINAL_STATE: 未找到结果但结果索引不是-1");
        // 状态特征3：如果未找到目标值，数组中确实不应存在该目标值
        // 验证数组中确实没有目标值（二分查找正确性验证）
        bool found_in_array = false;
        for (int i = 0; i < n; i++)
        {
            if (nums[i] == target)
            {
                found_in_array = true;
                break;
            }
        }
        assert(!found_in_array && "FINAL_STATE: 未找到目标值但数组中存在该值");
    }

    // 状态特征4：搜索继续标志必须为false（算法已终止）
    assert(continue_search == false || result_index != -1 && "FINAL_STATE: 算法完成但搜索继续标志为true且未找到结果");

    // 状态特征5：验证二分查找的不变量（搜索区间性质）
    // 二分查找结束后，left应该指向第一个大于等于target的位置（如果target存在，则是target的位置）
    // 这里我们验证一些基本性质
    if (result_index != -1)
    {
        // 如果找到目标值，验证目标值确实在数组中
        assert(nums[result_index] == target && "FINAL_STATE: 最终状态结果索引对应值不等于目标值");
    }

    // 状态特征6：验证搜索边界的合理性
    // left应该在0到n之间，right在-1到n-1之间
    assert(left >= 0 && left <= n && "FINAL_STATE: 最终状态左指针越界");
    assert(right >= -1 && right < n && "FINAL_STATE: 最终状态右指针越界");

    // 约束目的：验证算法最终收敛状态，确保二分查找结果正确
    goto RETURN_RESULT; // 跳转至返回结果动作

RETURN_RESULT:
    // 专门执行算法最终返回
    // 注意：RETURN_RESULT标签仅包含return语句，无其他业务逻辑
    return result_index; // 返回结果索引（找到则为索引，未找到则为-1）
}

// ====================== 测试主函数 ======================
int main()
{
    cout << "测试有序数组二分查找目标值算法" << endl
         << endl;

    // 测试用例1：常规情况 - 目标值存在
    cout << "测试用例1：常规情况 - 目标值存在" << endl;
    vector<int> nums1 = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19};
    int target1 = 7;
    cout << "有序数组: ";
    for (int num : nums1)
        cout << num << " ";
    cout << endl;
    cout << "目标值: " << target1 << endl;

    int result1 = binary_search(nums1, target1);
    cout << "找到的索引: " << result1 << endl;
    cout << "对应元素: " << (result1 != -1 ? to_string(nums1[result1]) : "未找到") << endl;

    assert(result1 == 3); // 7在索引3位置
    cout << "通过！" << endl
         << endl;

    // 测试用例2：边界情况 - 目标值在开头
    cout << "测试用例2：目标值在开头" << endl;
    vector<int> nums2 = {2, 4, 6, 8, 10, 12, 14, 16};
    int target2 = 2;
    cout << "有序数组: ";
    for (int num : nums2)
        cout << num << " ";
    cout << endl;
    cout << "目标值: " << target2 << endl;

    int result2 = binary_search(nums2, target2);
    cout << "找到的索引: " << result2 << endl;
    cout << "对应元素: " << (result2 != -1 ? to_string(nums2[result2]) : "未找到") << endl;

    assert(result2 == 0); // 2在索引0位置
    cout << "通过！" << endl
         << endl;

    // 测试用例3：边界情况 - 目标值在末尾
    cout << "测试用例3：目标值在末尾" << endl;
    vector<int> nums3 = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    int target3 = 10;
    cout << "有序数组: ";
    for (int num : nums3)
        cout << num << " ";
    cout << endl;
    cout << "目标值: " << target3 << endl;

    int result3 = binary_search(nums3, target3);
    cout << "找到的索引: " << result3 << endl;
    cout << "对应元素: " << (result3 != -1 ? to_string(nums3[result3]) : "未找到") << endl;

    assert(result3 == 9); // 10在索引9位置
    cout << "通过！" << endl
         << endl;

    // 测试用例4：目标值不存在
    cout << "测试用例4：目标值不存在" << endl;
    vector<int> nums4 = {1, 3, 5, 7, 9, 11};
    int target4 = 8;
    cout << "有序数组: ";
    for (int num : nums4)
        cout << num << " ";
    cout << endl;
    cout << "目标值: " << target4 << endl;

    int result4 = binary_search(nums4, target4);
    cout << "找到的索引: " << result4 << " (应为-1，表示未找到)" << endl;

    assert(result4 == -1); // 8不存在于数组中
    cout << "通过！" << endl
         << endl;

    // 测试用例5：空数组
    cout << "测试用例5：空数组" << endl;
    vector<int> nums5 = {};
    int target5 = 5;
    cout << "有序数组: (空)" << endl;
    cout << "目标值: " << target5 << endl;

    int result5 = binary_search(nums5, target5);
    cout << "找到的索引: " << result5 << " (应为-1，表示未找到)" << endl;

    assert(result5 == -1); // 空数组中任何值都不存在
    cout << "通过！" << endl
         << endl;

    // 测试用例6：只有一个元素的数组
    cout << "测试用例6：只有一个元素的数组" << endl;
    vector<int> nums6 = {42};
    int target6 = 42;
    cout << "有序数组: ";
    for (int num : nums6)
        cout << num << " ";
    cout << endl;
    cout << "目标值: " << target6 << endl;

    int result6 = binary_search(nums6, target6);
    cout << "找到的索引: " << result6 << endl;
    cout << "对应元素: " << (result6 != -1 ? to_string(nums6[result6]) : "未找到") << endl;

    assert(result6 == 0); // 42在索引0位置
    cout << "通过！" << endl
         << endl;

    // 测试用例7：重复元素的情况
    cout << "测试用例7：重复元素的情况" << endl;
    vector<int> nums7 = {1, 2, 2, 2, 3, 4, 5};
    int target7 = 2;
    cout << "有序数组: ";
    for (int num : nums7)
        cout << num << " ";
    cout << endl;
    cout << "目标值: " << target7 << endl;

    int result7 = binary_search(nums7, target7);
    cout << "找到的索引: " << result7 << endl;
    cout << "对应元素: " << (result7 != -1 ? to_string(nums7[result7]) : "未找到") << endl;

    // 二分查找可能返回任意一个等于目标值的索引，这里我们只验证找到的元素确实等于目标值
    assert(result7 != -1 && nums7[result7] == target7);
    cout << "通过！找到的索引是" << result7 << "，对应元素" << nums7[result7] << endl
         << endl;

    // 测试用例8：较大规模测试
    cout << "测试用例8：较大规模测试" << endl;
    vector<int> nums8;
    for (int i = 0; i < 1000; i++)
    {
        nums8.push_back(i * 2); // 偶数序列：0, 2, 4, ..., 1998
    }
    int target8 = 500;
    cout << "有序数组: 0到1998的偶数序列" << endl;
    cout << "目标值: " << target8 << endl;

    int result8 = binary_search(nums8, target8);
    cout << "找到的索引: " << result8 << endl;
    cout << "对应元素: " << (result8 != -1 ? to_string(nums8[result8]) : "未找到") << endl;

    // 500是偶数，应该在数组中
    assert(result8 == 250); // 250*2=500
    cout << "通过！" << endl
         << endl;

    cout << "所有测试用例通过！有序数组二分查找算法实现正确。" << endl;

    return 0;
}