#include <iostream>
#include <vector>
#include <cassert>
#include <algorithm>
#include <stack>

using namespace std;

// 快速排序：对输入vector<int>排序，返回升序序列
// 输入参数：待排序的整数序列
// 输出参数：排序后的升序序列
// 核心思想：通过分区操作将序列分为小于基准和大于基准的两部分，递归处理子序列
vector<int> quick_sort(vector<int> input_list)
{
    // ====================== 核心变量声明 ======================
    vector<int> sorted_list;       // 用途：存储排序后的结果序列；数据来源：输入序列的副本；生命周期：整个算法执行期间
    vector<int> start_index_stack; // 用途：存储需要排序的子序列起始索引（子问题参数）；数据来源：DIVIDE_SORT动作压栈；生命周期：整个算法执行期间
    vector<int> end_index_stack;   // 用途：存储需要排序的子序列结束索引（子问题参数）；数据来源：DIVIDE_SORT动作压栈；生命周期：整个算法执行期间
    int current_start_index;       // 用途：当前正在处理的子序列起始索引；数据来源：从栈中弹出或初始值0；生命周期：当前分区迭代期间
    int current_end_index;         // 用途：当前正在处理的子序列结束索引；数据来源：从栈中弹出或初始值n-1；生命周期：当前分区迭代期间
    int pivot_index;               // 用途：基准元素的最终正确位置索引；数据来源：PARTITION操作计算结果；生命周期：当前分区迭代期间
    int pivot_value;               // 用途：基准元素的值；数据来源：从当前子序列中选择；生命周期：当前分区迭代期间
    int i;                         // 用途：左指针，指向小于基准区域的最后一个元素；数据来源：PARTITION操作中初始化；生命周期：单次分区操作期间
    int j;                         // 用途：右指针，用于遍历子序列元素；数据来源：PARTITION操作中初始化；生命周期：单次分区操作期间
    int temp;                      // 用途：临时变量，用于元素交换操作；数据来源：交换操作时临时赋值；生命周期：单次交换操作期间
    int n;                         // 用途：输入序列的长度；数据来源：输入序列的size()；生命周期：整个算法执行期间
    bool stack_empty;              // 用途：标记自定义栈是否为空，控制算法主循环；数据来源：检查栈长度；生命周期：算法主循环期间

// ====================== 算法开始 ======================
INIT:
    // 目的：初始化算法所需的核心变量和数据结构
    // 变量关联：sorted_list接收输入序列，栈结构初始化为空，n记录序列长度
    // 全局作用：为快速排序的主循环和分区操作准备初始状态
    sorted_list = input_list;                 // 复制输入序列，避免修改原始数据
    n = static_cast<int>(sorted_list.size()); // 获取序列长度，用于后续边界检查
    start_index_stack.clear();                // 清空起始索引栈，确保初始状态为空
    end_index_stack.clear();                  // 清空结束索引栈，确保初始状态为空
    goto STATE_0;                             // 跳转至初始状态断言：验证变量初始化合法性

STATE_0:
    // 断言依据：初始化后必须确保sorted_list与输入序列长度一致
    // 状态特征1：sorted_list长度等于输入序列长度（数据复制正确性验证）
    assert(sorted_list.size() == input_list.size() && "STATE_0: 序列复制后长度不一致");
    // 状态特征2：自定义栈初始状态必须为空（确保算法从干净状态开始）
    assert(start_index_stack.empty() && "STATE_0: 起始索引栈初始状态非空");
    assert(end_index_stack.empty() && "STATE_0: 结束索引栈初始状态非空");
    // 约束目的：验证算法初始化的正确性，避免因初始化错误导致后续逻辑异常
    goto PUSH_INITIAL_PROBLEM; // 跳转至初始子问题入栈动作

PUSH_INITIAL_PROBLEM:
    // 目的：将整个序列作为初始子问题压入自定义栈
    // 变量关联：start_index_stack存储子序列起始索引，end_index_stack存储子序列结束索引
    // 全局作用：启动快速排序的主循环，确保整个序列被处理
    // 注意：快速排序是递归算法的迭代实现，通过栈存储待处理的子序列
    if (n > 0)
    {                                     // 只有非空序列才需要入栈排序
        start_index_stack.push_back(0);   // 将整个序列的起始索引0压入栈
        end_index_stack.push_back(n - 1); // 将整个序列的结束索引n-1压入栈
    }
    goto STATE_1; // 跳转至初始问题入栈后的状态断言

STATE_1:
    // 断言依据：初始子问题入栈后，栈长度必须一致且反映待处理序列范围
    // 状态特征1：起始索引栈与结束索引栈长度相等（数据结构一致性验证）
    assert(start_index_stack.size() == end_index_stack.size() && "STATE_1: 起始索引栈与结束索引栈长度不一致");
    // 状态特征2：如果序列非空，栈中应有一个子问题；如果序列为空，栈应为空
    if (n > 0)
    {
        assert(start_index_stack.size() == 1 && "STATE_1: 非空序列入栈后栈长度不为1");
        assert(start_index_stack.back() == 0 && "STATE_1: 起始索引栈顶元素不是0");
        assert(end_index_stack.back() == n - 1 && "STATE_1: 结束索引栈顶元素不是n-1");
    }
    else
    {
        assert(start_index_stack.empty() && "STATE_1: 空序列入栈后栈非空");
        assert(end_index_stack.empty() && "STATE_1: 空序列入栈后栈非空");
    }
    // 约束目的：验证初始子问题入栈的正确性，确保算法从正确的起点开始
    goto CHECK_STACK; // 跳转至栈检查动作，开始主循环

CHECK_STACK:
    // 目的：检查自定义栈是否为空，决定算法继续执行还是结束
    // 变量关联：stack_empty标记栈空状态，控制主循环流程
    // 全局作用：控制快速排序的迭代过程，栈空表示所有子问题已处理完毕
    // 注意：这是算法的主循环控制点，每次分区操作后都会回到这里
    stack_empty = start_index_stack.empty(); // 检查起始索引栈是否为空
    if (stack_empty)
    {                     // 如果栈为空，表示所有子序列已处理完毕
        goto FINAL_STATE; // 跳转至最终状态验证，准备返回结果
    }
    else
    {
        goto POP_STACK; // 跳转至弹出栈顶子问题动作，继续处理
    }

POP_STACK:
    // 目的：从栈中弹出当前需要处理的子序列范围
    // 变量关联：start_index_stack和end_index_stack提供子问题参数
    // 全局作用：获取下一个待排序的子序列，更新当前处理范围
    // 注意：栈的后进先出特性在这里被使用，但快速排序不依赖特定顺序
    current_end_index = end_index_stack.back();     // 从结束索引栈获取子序列结束索引
    end_index_stack.pop_back();                     // 弹出结束索引栈顶元素
    current_start_index = start_index_stack.back(); // 从起始索引栈获取子序列起始索引
    start_index_stack.pop_back();                   // 弹出起始索引栈顶元素
    goto STATE_2;                                   // 跳转至栈弹出后的状态断言

STATE_2:
    // 断言依据：弹出栈顶元素后，当前子序列索引必须满足合法范围约束
    // 状态特征1：当前起始索引必须小于等于当前结束索引（有效子序列条件）
    assert(current_start_index <= current_end_index && "STATE_2: 弹出子序列的起始索引大于结束索引");
    // 状态特征2：当前索引必须在原序列有效范围内（避免越界访问）
    assert(current_start_index >= 0 && current_start_index < n && "STATE_2: 当前起始索引越界");
    assert(current_end_index >= 0 && current_end_index < n && "STATE_2: 当前结束索引越界");
    // 状态特征3：栈弹出操作后，两个栈的长度仍然相等（数据结构一致性）
    assert(start_index_stack.size() == end_index_stack.size() && "STATE_2: 栈弹出后起始索引栈与结束索引栈长度不一致");
    // 约束目的：验证栈弹出操作的正确性和子序列参数的合法性
    goto CHECK_BASE_CASE; // 跳转至基础情况检查动作

CHECK_BASE_CASE:
    // 目的：检查当前子序列是否需要进一步处理（基础情况判断）
    // 变量关联：current_start_index和current_end_index确定子序列范围
    // 全局作用：识别递归终止条件，避免对单元素或空子序列进行不必要操作
    // 注意：这是快速排序递归算法的边界条件处理
    if (current_start_index >= current_end_index)
    {                     // 子序列长度为0或1（已有序）
        goto CHECK_STACK; // 跳转回栈检查，处理下一个子问题
    }
    else
    {
        goto CHOOSE_PIVOT; // 跳转至选择基准元素动作，开始分区操作
    }

CHOOSE_PIVOT:
    // 目的：选择当前子序列的基准元素，为分区操作做准备
    // 变量关联：pivot_value存储基准元素值，pivot_index记录基准位置
    // 全局作用：确定分区操作的比较基准，影响算法性能和分区结果
    // 注意：这里选择子序列中间位置的元素作为基准，平衡最坏情况概率
    pivot_index = current_start_index + (current_end_index - current_start_index) / 2; // 选择中间索引作为基准位置
    pivot_value = sorted_list[pivot_index];                                            // 获取基准元素的值
    goto STATE_3;                                                                      // 跳转至基准选择后的状态断言

STATE_3:
    // 断言依据：基准索引必须在当前子序列有效范围内，基准值必须存在
    // 状态特征1：基准索引在当前子序列起始和结束索引之间（合法性验证）
    assert(pivot_index >= current_start_index && pivot_index <= current_end_index && "STATE_3: 基准索引不在子序列范围内");
    // 状态特征2：基准值必须等于序列中对应位置的元素值（数据一致性验证）
    assert(pivot_value == sorted_list[pivot_index] && "STATE_3: 基准值与序列中对应位置元素不一致");
    // 状态特征3：基准索引必须在原序列有效范围内（避免越界）
    assert(pivot_index >= 0 && pivot_index < n && "STATE_3: 基准索引越界");
    // 约束目的：验证基准选择操作的合法性，确保分区操作基于有效基准
    goto INIT_PARTITION; // 跳转至分区初始化动作

INIT_PARTITION:
    // 目的：初始化分区操作所需的指针和临时变量
    // 变量关联：i初始化为起始索引前一位，j从起始索引开始遍历
    // 全局作用：为双指针分区算法准备初始状态，确保分区逻辑正确执行
    // 注意：i指向小于基准区域的最后一个元素，j用于遍历整个子序列
    i = current_start_index - 1; // i初始化为起始索引前一位（小于基准区域为空）
    j = current_start_index;     // j从起始索引开始，将遍历到结束索引
    goto STATE_4;                // 跳转至分区初始化后的状态断言

STATE_4:
    // 断言依据：分区初始化后，指针i和j必须满足特定位置关系
    // 状态特征1：指针i必须等于起始索引减1（指向小于基准区域的边界）
    assert(i == current_start_index - 1 && "STATE_4: 分区初始化后指针i位置错误");
    // 状态特征2：指针j必须等于起始索引（准备从子序列开头遍历）
    assert(j == current_start_index && "STATE_4: 分区初始化后指针j位置错误");
    // 状态特征3：指针i和j的差值必须为1（初始位置关系验证）
    assert(j - i == 1 && "STATE_4: 分区初始化后指针i和j的相对位置错误");
    // 约束目的：验证分区指针初始化的正确性，确保分区逻辑的起点正确
    goto PARTITION_LOOP_START; // 跳转至分区循环开始动作

PARTITION_LOOP_START:
    // 目的：开始遍历子序列，将元素与基准值比较并移动到正确区域
    // 变量关联：j指针用于遍历，i指针标记小于基准区域的边界
    // 全局作用：执行分区操作的核心循环，实现原地重排算法
    // 注意：循环结束时，j指针将到达结束索引位置
    if (j <= current_end_index)
    {                           // 当j未超过子序列结束索引时继续遍历
        goto PARTITION_COMPARE; // 跳转至元素比较动作
    }
    else
    {
        goto PARTITION_SWAP_PIVOT; // 跳转至基准元素最终放置动作
    }

PARTITION_COMPARE:
    // 目的：比较当前元素与基准值，决定是否将其移动到小于基准区域
    // 变量关联：j指向当前元素，i指向小于基准区域的最后一个元素
    // 全局作用：实现快速排序的核心分区逻辑，原地重排元素
    // 注意：这里实现了Lomuto分区方案，简单但非最优性能
    if (sorted_list[j] <= pivot_value)
    {              // 如果当前元素小于等于基准值
        i = i + 1; // 扩展小于基准区域：i指针右移一位
        // 交换i和j位置的元素，将当前元素移动到小于基准区域
        temp = sorted_list[i];           // 临时保存i位置的元素
        sorted_list[i] = sorted_list[j]; // 将j位置的元素移动到i位置
        sorted_list[j] = temp;           // 将临时保存的元素放到j位置

        // 如果基准元素被移动，需要更新基准索引
        if (i == pivot_index)
        {                    // 如果基准元素被移动（从i位置移动到j位置）
            pivot_index = j; // 更新基准索引为新的位置
        }
        else if (j == pivot_index)
        {                    // 如果基准元素被移动（从j位置移动到i位置）
            pivot_index = i; // 更新基准索引为新的位置
        }
    }
    j = j + 1;    // j指针右移，处理下一个元素
    goto STATE_5; // 跳转至分区循环中的状态断言

STATE_5:
    // 断言依据：分区循环中，指针必须满足特定约束条件
    // 状态特征1：指针i必须始终在指针j的左侧或相同位置（分区区域正确性）
    assert(i < j && "STATE_5: 分区循环中指针i位置超过指针j");
    // 状态特征2：指针j必须在合理范围内（未超过子序列边界加1）
    assert(j >= current_start_index && j <= current_end_index + 1 && "STATE_5: 分区循环中指针j越界");
    // 状态特征3：指针i必须在合理范围内（未超过子序列边界）
    assert(i >= current_start_index - 1 && i <= current_end_index && "STATE_5: 分区循环中指针i越界");
    // 状态特征4：基准索引必须在当前子序列范围内（基准位置合法性）
    assert(pivot_index >= current_start_index && pivot_index <= current_end_index && "STATE_5: 基准索引越界");
    // 约束目的：验证分区循环中指针位置的合法性，确保分区逻辑正确执行
    goto PARTITION_LOOP_START; // 跳转回分区循环开始，继续遍历

PARTITION_SWAP_PIVOT:
    // 目的：将基准元素交换到最终正确位置（i+1位置）
    // 变量关联：i指向小于基准区域的最后一个元素，基准需要放在i+1位置
    // 全局作用：完成分区操作，确保基准元素在最终排序位置
    // 注意：循环结束后，i指向小于基准区域的最后一个元素，基准应放在i+1位置
    // 交换基准元素到正确位置
    temp = sorted_list[i + 1];                     // 临时保存i+1位置的元素
    sorted_list[i + 1] = sorted_list[pivot_index]; // 将基准元素移动到i+1位置
    sorted_list[pivot_index] = temp;               // 将临时保存的元素放到原基准位置
    pivot_index = i + 1;                           // 更新基准索引为最终正确位置
    goto STATE_6;                                  // 跳转至分区完成后的状态断言

STATE_6:
    // 断言依据：分区完成后，基准元素必须位于最终正确位置
    // 状态特征1：基准元素最终位置必须在当前子序列范围内（合法性验证）
    assert(pivot_index >= current_start_index && pivot_index <= current_end_index && "STATE_6: 分区后基准索引越界");
    // 状态特征2：基准元素最终位置必须等于i+1（分区算法正确性验证）
    assert(pivot_index == i + 1 && "STATE_6: 分区后基准索引不等于i+1");
    // 状态特征3：基准元素值必须等于序列中对应位置的元素值（数据一致性）
    assert(pivot_value == sorted_list[pivot_index] && "STATE_6: 分区后基准值与序列中对应位置元素不一致");
    // 状态特征4：基准左侧元素必须都小于等于基准值（分区正确性验证）
    for (int k = current_start_index; k < pivot_index; k++)
    {
        assert(sorted_list[k] <= pivot_value && "STATE_6: 分区后基准左侧存在大于基准的元素");
    }
    // 状态特征5：基准右侧元素必须都大于基准值（分区正确性验证）
    for (int k = pivot_index + 1; k <= current_end_index; k++)
    {
        assert(sorted_list[k] > pivot_value && "STATE_6: 分区后基准右侧存在小于等于基准的元素");
    }
    // 约束目的：验证分区操作的正确性，确保基准元素在正确位置且两侧元素满足分区条件
    goto DIVIDE_SORT; // 跳转至子问题划分动作

DIVIDE_SORT:
    // 目的：将分区后的两个子序列（基准左侧和右侧）压入栈中待处理
    // 变量关联：current_start_index、pivot_index、current_end_index定义子序列范围
    // 全局作用：实现快速排序的递归逻辑（迭代版本），继续处理更小的子问题
    // 注意：先压入右侧子序列，再压入左侧子序列，保证处理顺序（非必需但常见）

    // 压入右侧子序列（基准右侧，较大元素区域）
    if (pivot_index + 1 < current_end_index)
    {                                                 // 右侧子序列长度大于1才需要处理
        start_index_stack.push_back(pivot_index + 1); // 右侧子序列起始索引
        end_index_stack.push_back(current_end_index); // 右侧子序列结束索引
    }

    // 压入左侧子序列（基准左侧，较小元素区域）
    if (current_start_index < pivot_index - 1)
    {                                                     // 左侧子序列长度大于1才需要处理
        start_index_stack.push_back(current_start_index); // 左侧子序列起始索引
        end_index_stack.push_back(pivot_index - 1);       // 左侧子序列结束索引
    }
    goto STATE_7; // 跳转至子问题划分后的状态断言

STATE_7:
    // 断言依据：子问题划分后，栈状态必须满足特定约束
    // 状态特征1：起始索引栈与结束索引栈长度相等（数据结构一致性）
    assert(start_index_stack.size() == end_index_stack.size() && "STATE_7: 子问题划分后栈长度不一致");
    // 状态特征2：栈中所有子序列索引必须在有效范围内（避免越界）
    for (size_t k = 0; k < start_index_stack.size(); k++)
    {
        assert(start_index_stack[k] >= 0 && start_index_stack[k] < n && "STATE_7: 栈中起始索引越界");
        assert(end_index_stack[k] >= 0 && end_index_stack[k] < n && "STATE_7: 栈中结束索引越界");
        assert(start_index_stack[k] <= end_index_stack[k] && "STATE_7: 栈中起始索引大于结束索引");
    }
    // 状态特征3：栈中不应包含单元素子序列（已在CHECK_BASE_CASE中过滤）
    for (size_t k = 0; k < start_index_stack.size(); k++)
    {
        assert(end_index_stack[k] - start_index_stack[k] >= 1 && "STATE_7: 栈中存在长度小于2的子序列");
    }
    // 约束目的：验证子问题划分的正确性，确保栈中存储的待处理子问题合法
    goto CHECK_STACK; // 跳转回栈检查动作，继续处理下一个子问题

FINAL_STATE:
    // 目的：验证算法完成后的最终收敛状态
    // 断言依据：快速排序算法完成后，序列必须有序且长度不变
    // 状态特征1：输出序列长度必须等于输入序列长度（数据完整性验证）
    assert(sorted_list.size() == input_list.size() && "STATE_8: 输出序列长度与输入不一致");
    // 状态特征2：输出序列必须按非降序排列（升序排序正确性验证）
    // 全局作用：确保算法执行完毕后输出合法，避免未排序完成就返回
    for (size_t k = 1; k < sorted_list.size(); k++)
    {
        assert(sorted_list[k] >= sorted_list[k - 1] && "STATE_8: 输出序列未按升序排序（最终状态非法）");
    }
    // 状态特征3：自定义栈必须为空（所有子问题已处理完毕）
    assert(start_index_stack.empty() && "STATE_8: 算法完成后起始索引栈非空");
    assert(end_index_stack.empty() && "STATE_8: 算法完成后结束索引栈非空");
    // 约束目的：验证算法最终收敛状态，确保排序结果正确且算法完全终止
    goto RETURN_RESULT; // 跳转至返回结果动作

RETURN_RESULT:
    // 专门执行算法最终返回
    // 注意：RETURN_RESULT标签仅包含return语句，无其他业务逻辑
    return sorted_list; // 返回排序后的序列
}

// ====================== 测试主函数 ======================
int main()
{
    // 测试用例1：常规无序序列
    // 目的：验证快速排序对普通无序序列的排序能力
    cout << "测试用例1：常规无序序列" << endl;
    vector<int> test1 = {64, 34, 25, 12, 22, 11, 90};
    cout << "输入序列: ";
    for (int num : test1)
        cout << num << " ";
    cout << endl;

    vector<int> result1 = quick_sort(test1);
    cout << "排序结果: ";
    for (int num : result1)
        cout << num << " ";
    cout << endl;

    // 验证排序结果正确性
    vector<int> expected1 = {11, 12, 22, 25, 34, 64, 90};
    assert(result1 == expected1 && "测试用例1：排序结果不正确");
    cout << "测试用例1通过！" << endl
         << endl;

    // 测试用例2：已排序序列（边界场景）
    // 目的：验证快速排序对已排序序列的处理能力（避免最坏情况性能问题）
    cout << "测试用例2：已排序序列" << endl;
    vector<int> test2 = {1, 2, 3, 4, 5, 6, 7, 8};
    cout << "输入序列: ";
    for (int num : test2)
        cout << num << " ";
    cout << endl;

    vector<int> result2 = quick_sort(test2);
    cout << "排序结果: ";
    for (int num : result2)
        cout << num << " ";
    cout << endl;

    // 验证排序结果正确性
    vector<int> expected2 = {1, 2, 3, 4, 5, 6, 7, 8};
    assert(result2 == expected2 && "测试用例2：排序结果不正确");
    cout << "测试用例2通过！" << endl
         << endl;

    // 测试用例3：逆序序列（边界场景）
    // 目的：验证快速排序对逆序序列的处理能力（避免最坏情况性能问题）
    cout << "测试用例3：逆序序列" << endl;
    vector<int> test3 = {9, 8, 7, 6, 5, 4, 3, 2, 1};
    cout << "输入序列: ";
    for (int num : test3)
        cout << num << " ";
    cout << endl;

    vector<int> result3 = quick_sort(test3);
    cout << "排序结果: ";
    for (int num : result3)
        cout << num << " ";
    cout << endl;

    // 验证排序结果正确性
    vector<int> expected3 = {1, 2, 3, 4, 5, 6, 7, 8, 9};
    assert(result3 == expected3 && "测试用例3：排序结果不正确");
    cout << "测试用例3通过！" << endl
         << endl;

    // 测试用例4：包含重复元素的序列（边界场景）
    // 目的：验证快速排序对包含重复元素序列的处理能力
    cout << "测试用例4：包含重复元素的序列" << endl;
    vector<int> test4 = {5, 2, 8, 2, 5, 8, 1, 2, 5};
    cout << "输入序列: ";
    for (int num : test4)
        cout << num << " ";
    cout << endl;

    vector<int> result4 = quick_sort(test4);
    cout << "排序结果: ";
    for (int num : result4)
        cout << num << " ";
    cout << endl;

    // 验证排序结果正确性
    vector<int> expected4 = {1, 2, 2, 2, 5, 5, 5, 8, 8};
    assert(result4 == expected4 && "测试用例4：排序结果不正确");
    cout << "测试用例4通过！" << endl
         << endl;

    // 测试用例5：空序列（边界场景）
    // 目的：验证快速排序对空序列的处理能力
    cout << "测试用例5：空序列" << endl;
    vector<int> test5 = {};
    cout << "输入序列: (空)" << endl;

    vector<int> result5 = quick_sort(test5);
    cout << "排序结果: ";
    for (int num : result5)
        cout << num << " ";
    cout << "(空)" << endl;

    // 验证排序结果正确性
    assert(result5.empty() && "测试用例5：空序列排序结果非空");
    cout << "测试用例5通过！" << endl
         << endl;

    // 测试用例6：单元素序列（边界场景）
    // 目的：验证快速排序对单元素序列的处理能力
    cout << "测试用例6：单元素序列" << endl;
    vector<int> test6 = {42};
    cout << "输入序列: ";
    for (int num : test6)
        cout << num << " ";
    cout << endl;

    vector<int> result6 = quick_sort(test6);
    cout << "排序结果: ";
    for (int num : result6)
        cout << num << " ";
    cout << endl;

    // 验证排序结果正确性
    vector<int> expected6 = {42};
    assert(result6 == expected6 && "测试用例6：排序结果不正确");
    cout << "测试用例6通过！" << endl
         << endl;

    cout << "所有测试用例通过！快速排序算法实现正确。" << endl;

    return 0;
}