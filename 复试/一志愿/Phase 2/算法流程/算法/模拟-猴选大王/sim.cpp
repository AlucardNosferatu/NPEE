#include <iostream>
#include <vector>
#include <cassert>
#include <numeric>

using namespace std;

// 约瑟夫问题（猴子选大王）：基于数组模拟的求解算法
// 输入参数：n - 猴子总数（从1到n编号），m - 报数淘汰值（报到m的猴子被淘汰）
// 输出参数：最后剩下的猴子编号（大王编号）
// 核心思想：使用数组模拟猴子圈，依次报数淘汰，直到只剩一只猴子
int josephus_problem(int n, int m)
{
    // ====================== 核心变量声明 ======================
    vector<bool> monkeys; // 用途：存储猴子是否在圈内的状态；数据来源：根据n初始化；生命周期：整个算法执行期间
    int current_index;    // 用途：当前报数的猴子索引；数据来源：从0开始，每次移动；生命周期：算法主循环期间
    int count;            // 用途：当前报数计数；数据来源：从1开始，报到m重置；生命周期：单次报数循环期间
    int remaining;        // 用途：圈内剩余猴子数量；数据来源：初始为n，淘汰时减1；生命周期：整个算法执行期间
    int next_index;       // 用途：下一个要检查的猴子索引；数据来源：current_index按规则移动；生命周期：查找下一个在圈猴子期间
    bool found_next;      // 用途：是否找到下一个在圈猴子的标志；数据来源：查找逻辑结果；生命周期：查找过程中

// ====================== 算法开始 ======================
INIT:
    // 目的：初始化算法所需的核心变量和数据结构
    // 变量关联：monkeys数组表示所有猴子状态，current_index从0开始，count从1开始
    // 全局作用：为约瑟夫问题的模拟过程准备初始状态
    monkeys = vector<bool>(n, true); // 初始化n个猴子，都在圈内（true表示在圈内）
    current_index = 0;               // 从第一个猴子（索引0）开始报数
    count = 1;                       // 报数从1开始
    remaining = n;                   // 初始时所有猴子都在圈内
    next_index = 0;                  // 下一个要检查的索引初始化为0
    found_next = false;              // 初始时未找到下一个在圈猴子
    goto STATE_0;                    // 跳转至初始状态断言：验证变量初始化合法性

STATE_0:
    // 断言依据：初始化后必须确保核心变量处于合法初始状态
    // 状态特征1：猴子数组长度必须等于n（数组初始化正确性验证）
    assert(monkeys.size() == static_cast<size_t>(n) && "STATE_0: 猴子数组长度不等于n");
    // 状态特征2：所有猴子初始状态必须在圈内（true）
    for (int i = 0; i < n; i++)
    {
        assert(monkeys[i] == true && "STATE_0: 猴子初始状态不在圈内");
    }
    // 状态特征3：当前索引必须为0（从第一个猴子开始）
    assert(current_index == 0 && "STATE_0: 当前索引初始状态不是0");
    // 状态特征4：报数计数必须为1（从1开始报数）
    assert(count == 1 && "STATE_0: 报数计数初始状态不是1");
    // 状态特征5：剩余猴子数量必须等于n（初始状态正确性）
    assert(remaining == n && "STATE_0: 剩余猴子数量初始状态不等于n");
    // 状态特征6：n和m必须是正整数（约瑟夫问题的前提条件）
    assert(n > 0 && "STATE_0: 猴子数量n必须为正整数");
    assert(m > 0 && "STATE_0: 报数淘汰值m必须为正整数");
    // 约束目的：验证算法初始化的正确性，确保从正确状态开始模拟
    goto CHECK_REMAINING; // 跳转至检查剩余猴子数量动作

CHECK_REMAINING:
    // 目的：检查圈内剩余猴子数量，判断是否已选出大王
    // 变量关联：remaining记录当前圈内猴子数量
    // 全局作用：控制算法的主循环，当只剩一只猴子时结束模拟
    // 注意：这是算法的主循环控制点，每次淘汰猴子后都会检查
    if (remaining == 1)
    {                            // 如果只剩一只猴子，选出大王
        goto START_FINAL_SEARCH; // 跳转至开始最终查找动作
    }
    else
    {                              // 否则继续报数淘汰过程
        goto CHECK_CURRENT_MONKEY; // 跳转至检查当前猴子状态动作
    }

CHECK_CURRENT_MONKEY:
    // 目的：检查当前索引位置的猴子是否在圈内
    // 变量关联：current_index指向当前猴子，monkeys数组存储状态
    // 全局作用：确保报数只在在圈猴子中进行，跳过已被淘汰的猴子
    // 注意：由于猴子可能被淘汰，需要跳过不在圈内的猴子
    if (monkeys[current_index] == true)
    {                          // 如果当前猴子在圈内
        goto PROCESS_COUNTING; // 跳转至处理报数动作
    }
    else
    {                             // 如果当前猴子不在圈内（已被淘汰）
        goto MOVE_TO_NEXT_MONKEY; // 跳转至移动到下一个猴子动作
    }

PROCESS_COUNTING:
    // 目的：处理当前猴子的报数逻辑
    // 变量关联：count记录当前报数值，m是淘汰阈值
    // 全局作用：模拟报数过程，判断当前猴子是否应该被淘汰
    // 注意：这是约瑟夫问题的核心逻辑，决定猴子何时被淘汰
    if (count == m)
    {                          // 如果报数到m，淘汰当前猴子
        goto ELIMINATE_MONKEY; // 跳转至淘汰猴子动作
    }
    else
    {                      // 如果还没报到m，继续报数
        count = count + 1; // 报数加1
        goto STATE_1;      // 跳转至报数处理后的状态断言
    }

STATE_1:
    // 断言依据：报数处理后，计数状态必须满足特定约束
    // 状态特征1：报数计数必须在1到m之间（包括m，但淘汰时会立即处理）
    assert(count >= 1 && count <= m && "STATE_1: 报数计数超出有效范围");
    // 状态特征2：当前猴子必须在圈内（因为刚刚处理了报数）
    assert(monkeys[current_index] == true && "STATE_1: 当前猴子不在圈内但处理了报数");
    // 状态特征3：当前索引必须在有效范围内
    assert(current_index >= 0 && current_index < n && "STATE_1: 当前索引越界");
    // 状态特征4：剩余猴子数量必须大于1（否则不会进入报数处理）
    assert(remaining > 1 && "STATE_1: 剩余猴子数量为1但仍在报数");
    // 约束目的：验证报数处理逻辑的正确性，确保计数更新和状态一致性
    goto MOVE_TO_NEXT_MONKEY; // 跳转至移动到下一个猴子动作

MOVE_TO_NEXT_MONKEY:
    // 目的：移动到下一个猴子位置（模拟圆圈移动）
    // 变量关联：current_index表示当前位置，n是猴子总数
    // 全局作用：在圆圈中移动到下一个位置，处理环形结构
    // 注意：约瑟夫问题是环形问题，到达末尾后要回到开头
    current_index = (current_index + 1) % n; // 移动到下一个位置，使用取模实现环形
    goto STATE_2;                            // 跳转至移动后的状态断言

STATE_2:
    // 断言依据：移动到下一个猴子后，索引必须满足环形约束
    // 状态特征1：移动后的索引必须在0到n-1范围内（环形索引有效性）
    assert(current_index >= 0 && current_index < n && "STATE_2: 移动后索引越界");
    // 状态特征2：索引移动必须是环形递增（从i到(i+1)%n）
    // 注意：这里通过取模操作保证，不需要额外断言
    // 状态特征3：如果原索引是n-1，移动后必须是0（环形特性验证）
    // 约束目的：验证环形移动操作的正确性，确保模拟圆圈结构
    goto CHECK_REMAINING; // 跳转回检查剩余猴子数量动作，继续循环

ELIMINATE_MONKEY:
    // 目的：淘汰当前猴子（设置为不在圈内）
    // 变量关联：current_index指向要被淘汰的猴子，remaining减少
    // 全局作用：执行淘汰操作，减少圈内猴子数量
    // 注意：淘汰后需要重置报数计数，为下一个猴子从1开始报数
    monkeys[current_index] = false; // 将当前猴子标记为淘汰（不在圈内）
    remaining = remaining - 1;      // 剩余猴子数量减1
    count = 1;                      // 重置报数计数，下一个猴子从1开始报数
    goto STATE_3;                   // 跳转至淘汰后的状态断言

STATE_3:
    // 断言依据：淘汰猴子后，相关状态必须正确更新
    // 状态特征1：被淘汰的猴子状态必须为false（不在圈内）
    assert(monkeys[current_index] == false && "STATE_3: 淘汰后猴子状态仍为true");
    // 状态特征2：剩余猴子数量必须减少1
    // 注意：通过遍历统计验证剩余数量与remaining的一致性
    int actual_remaining = 0;
    for (int i = 0; i < n; i++)
    {
        if (monkeys[i] == true)
            actual_remaining++;
    }
    assert(actual_remaining == remaining && "STATE_3: 剩余猴子数量与数组状态不一致");
    // 状态特征3：报数计数必须重置为1
    assert(count == 1 && "STATE_3: 淘汰后报数计数未重置为1");
    // 状态特征4：剩余猴子数量必须大于0（不可能淘汰到0）
    assert(remaining > 0 && "STATE_3: 淘汰后剩余猴子数量为0");
    // 约束目的：验证淘汰操作的正确性，确保状态更新一致
    goto CHECK_REMAINING; // 跳转回检查剩余猴子数量动作

START_FINAL_SEARCH:
    // 目的：开始查找最终剩下的猴子（大王）
    // 变量关联：初始化查找变量
    // 全局作用：准备查找最终剩下的猴子
    next_index = 0;     // 从索引0开始查找
    found_next = false; // 重置找到标志
    goto STATE_4;       // 跳转至开始查找后的状态断言

STATE_4:
    // 断言依据：开始查找最终猴子后，必须确保查找变量初始状态正确
    // 状态特征1：剩余猴子数量必须为1（查找最终猴子的条件）
    assert(remaining == 1 && "STATE_4: 开始查找最终猴子时剩余猴子数量不为1");
    // 状态特征2：查找索引必须初始化为0
    assert(next_index == 0 && "STATE_4: 查找索引初始状态不是0");
    // 状态特征3：找到标志必须初始化为false
    assert(found_next == false && "STATE_4: 找到标志初始状态不是false");
    // 约束目的：验证开始查找操作的准备状态正确性
    goto CHECK_SEARCH_LOOP; // 跳转至检查查找循环条件动作

CHECK_SEARCH_LOOP:
    // 目的：检查查找循环是否继续
    // 变量关联：next_index表示当前检查位置，n是猴子总数
    // 全局作用：控制查找最终猴子的循环
    if (next_index < n)
    {                             // 如果还有猴子需要检查
        goto CHECK_MONKEY_STATUS; // 跳转至检查猴子状态动作
    }
    else
    {                               // 如果已检查完所有猴子
        goto COMPLETE_FINAL_SEARCH; // 跳转至完成查找动作
    }

CHECK_MONKEY_STATUS:
    // 目的：检查当前索引位置的猴子是否在圈内
    // 变量关联：next_index指向要检查的猴子，monkeys数组存储状态
    // 全局作用：在查找循环中检查每个猴子的状态
    if (monkeys[next_index] == true)
    {                               // 如果当前猴子在圈内
        found_next = true;          // 设置找到标志为true
        current_index = next_index; // 更新当前索引为找到的猴子
    }
    next_index = next_index + 1; // 移动到下一个猴子
    goto STATE_5;                // 跳转至检查猴子状态后的状态断言

STATE_5:
    // 断言依据：检查猴子状态后，必须确保变量更新正确
    // 状态特征1：查找索引必须递增1（移动逻辑正确性验证）
    assert(next_index >= 1 && next_index <= n && "STATE_5: 查找索引越界");
    // 状态特征2：如果找到猴子，找到标志必须为true，且当前索引必须正确
    if (found_next)
    {
        assert(current_index >= 0 && current_index < n && "STATE_5: 找到的猴子索引越界");
        assert(monkeys[current_index] == true && "STATE_5: 找到的猴子状态不为true");
    }
    // 约束目的：验证查找循环中状态更新的正确性
    goto CHECK_SEARCH_LOOP; // 跳转回检查查找循环条件动作

COMPLETE_FINAL_SEARCH:
    // 目的：完成查找操作，准备进入最终状态验证
    // 变量关联：计算大王编号，为最终状态验证做准备
    // 全局作用：这是查找完成后的最后一个动作标签
    int king_number = current_index + 1; // 计算大王编号（索引+1）
    goto FINAL_STATE;                    // 跳转至最终状态断言

FINAL_STATE:
    // 目的：验证算法完成后的最终收敛状态并返回结果
    // 根据任务要求：如果STATE_X已经是最终返回前的最后状态，不要单独分出一个FINAL_STATE
    // 这个STATE_X直接改名FINAL_STATE（代码不要分开，都写在这个FINAL_STATE下）就可以了！
    // 断言依据：约瑟夫问题算法完成后，必须满足特定最终状态

    // 状态特征1：必须找到在圈的猴子（因为remaining=1）
    assert(found_next == true && "FINAL_STATE: 未找到在圈的猴子但remaining=1");

    // 状态特征2：找到的猴子索引必须在有效范围内
    assert(current_index >= 0 && current_index < n && "FINAL_STATE: 找到的猴子索引越界");

    // 状态特征3：找到的猴子状态必须为true（在圈内）
    assert(monkeys[current_index] == true && "FINAL_STATE: 找到的猴子状态不为true");

    // 状态特征4：圈内应该只有一只猴子（remaining=1）
    // 通过遍历验证只有一只猴子状态为true
    int true_count = 0;
    int last_true_index = -1;
    for (int i = 0; i < n; i++)
    {
        if (monkeys[i] == true)
        {
            true_count++;
            last_true_index = i;
        }
    }
    assert(true_count == 1 && "FINAL_STATE: 圈内猴子数量不唯一");
    assert(last_true_index == current_index && "FINAL_STATE: 找到的猴子不是唯一在圈的猴子");

    // 状态特征5：圈内必须只剩一只猴子（大王选出条件）
    assert(remaining == 1 && "FINAL_STATE: 最终剩余猴子数量不为1");

    // 状态特征6：当前索引必须指向唯一在圈的猴子
    assert(monkeys[current_index] == true && "FINAL_STATE: 最终当前猴子不在圈内");

    // 状态特征7：有且只有一只猴子状态为true
    int final_true_count = 0;
    for (int i = 0; i < n; i++)
    {
        if (monkeys[i] == true)
            final_true_count++;
    }
    assert(final_true_count == 1 && "FINAL_STATE: 最终状态圈内猴子数量不唯一");

    // 状态特征8：报数计数必须为1（淘汰后重置，最终状态应为1）
    assert(count == 1 && "FINAL_STATE: 最终报数计数不为1");

    // 状态特征9：大王编号必须在1到n之间（转换为编号后验证）
    int king_number = current_index + 1; // 索引转换为编号（从1开始）
    assert(king_number >= 1 && king_number <= n && "FINAL_STATE: 大王编号超出有效范围");

    // 约束目的：验证算法最终收敛状态，确保约瑟夫问题求解正确
    goto RETURN_RESULT; // 跳转至返回结果动作

RETURN_RESULT:
    // 专门执行算法最终返回
    // 注意：RETURN_RESULT标签仅包含return语句，无其他业务逻辑
    return current_index + 1; // 返回大王编号（索引+1，因为猴子从1开始编号）
}

// ====================== 测试主函数 ======================
int main()
{
    // 测试用例1：经典约瑟夫问题（n=5, m=2）
    // 目的：验证经典约瑟夫问题的求解正确性
    cout << "测试用例1：经典约瑟夫问题（n=5, m=2）" << endl;
    int n1 = 5, m1 = 2;
    cout << "猴子数量n=" << n1 << ", 报数淘汰值m=" << m1 << endl;

    int result1 = josephus_problem(n1, m1);
    cout << "选出的大王编号: " << result1 << endl;

    // 验证结果正确性（根据约瑟夫问题公式或手动模拟验证）
    // 淘汰顺序：2, 4, 1, 5，最后剩下3
    int expected1 = 3;
    assert(result1 == expected1 && "测试用例1：大王编号不正确");
    cout << "测试用例1通过！" << endl
         << endl;

    // 测试用例2：m=1的特殊情况（逐个淘汰）
    // 目的：验证m=1时的特殊情况处理能力
    cout << "测试用例2：m=1的特殊情况（n=7, m=1）" << endl;
    int n2 = 7, m2 = 1;
    cout << "猴子数量n=" << n2 << ", 报数淘汰值m=" << m2 << endl;

    int result2 = josephus_problem(n2, m2);
    cout << "选出的大王编号: " << result2 << endl;

    // 验证结果正确性（m=1时最后一个猴子是大王）
    int expected2 = 7; // 从1开始报数，报到1就淘汰，最后剩下第7个
    assert(result2 == expected2 && "测试用例2：大王编号不正确");
    cout << "测试用例2通过！" << endl
         << endl;

    // 测试用例3：m=3的较大规模测试
    // 目的：验证算法对较大规模问题的处理能力
    cout << "测试用例3：较大规模问题（n=10, m=3）" << endl;
    int n3 = 10, m3 = 3;
    cout << "猴子数量n=" << n3 << ", 报数淘汰值m=" << m3 << endl;

    int result3 = josephus_problem(n3, m3);
    cout << "选出的大王编号: " << result3 << endl;

    // 验证结果正确性（根据已知约瑟夫问题结果）
    // 淘汰顺序：3, 6, 9, 2, 7, 1, 8, 5, 10，最后剩下4
    int expected3 = 4;
    assert(result3 == expected3 && "测试用例3：大王编号不正确");
    cout << "测试用例3通过！" << endl
         << endl;

    // 测试用例4：n=1的边界情况（只有一只猴子）
    // 目的：验证只有一只猴子时的边界情况处理
    cout << "测试用例4：只有一只猴子（n=1, m=5）" << endl;
    int n4 = 1, m4 = 5;
    cout << "猴子数量n=" << n4 << ", 报数淘汰值m=" << m4 << endl;

    int result4 = josephus_problem(n4, m4);
    cout << "选出的大王编号: " << result4 << endl;

    // 验证结果正确性（只有一只猴子时，它就是大王）
    int expected4 = 1;
    assert(result4 == expected4 && "测试用例4：大王编号不正确");
    cout << "测试用例4通过！" << endl
         << endl;

    // 测试用例5：n和m相等的情况
    // 目的：验证n和m相等时的特殊情况处理能力
    cout << "测试用例5：n和m相等（n=6, m=6）" << endl;
    int n5 = 6, m5 = 6;
    cout << "猴子数量n=" << n5 << ", 报数淘汰值m=" << m5 << endl;

    int result5 = josephus_problem(n5, m5);
    cout << "选出的大王编号: " << result5 << endl;

    // 验证结果正确性（根据模拟或公式计算）
    // 淘汰顺序：6, 5, 1, 3, 2，最后剩下4
    int expected5 = 4;
    assert(result5 == expected5 && "测试用例5：大王编号不正确");
    cout << "测试用例5通过！" << endl
         << endl;

    // 测试用例6：m大于n的情况
    // 目的：验证m大于n时的处理能力（环形报数特性）
    cout << "测试用例6：m大于n（n=4, m=7）" << endl;
    int n6 = 4, m6 = 7;
    cout << "猴子数量n=" << n6 << ", 报数淘汰值m=" << m6 << endl;

    int result6 = josephus_problem(n6, m6);
    cout << "选出的大王编号: " << result6 << endl;

    // 验证结果正确性（m=7相当于m=7%4=3，因为报数在环上进行）
    // 先计算等效的m值：7 % 4 = 3，所以问题等价于n=4, m=3
    // 淘汰顺序：3, 2, 4，最后剩下1
    int expected6 = 1;
    assert(result6 == expected6 && "测试用例6：大王编号不正确");
    cout << "测试用例6通过！" << endl
         << endl;

    // 测试用例7：较大规模测试（n=41, m=3）经典约瑟夫问题
    // 目的：验证经典历史问题（约瑟夫和他的朋友）的求解
    cout << "测试用例7：经典历史问题（n=41, m=3）" << endl;
    int n7 = 41, m7 = 3;
    cout << "猴子数量n=" << n7 << ", 报数淘汰值m=" << m7 << endl;

    int result7 = josephus_problem(n7, m7);
    cout << "选出的大王编号: " << result7 << endl;

    // 验证结果正确性（历史记载约瑟夫把自己和朋友安排在16和31位置得以存活）
    // 已知约瑟夫问题n=41, m=3的解是31
    int expected7 = 31;
    assert(result7 == expected7 && "测试用例7：大王编号不正确");
    cout << "测试用例7通过！" << endl
         << endl;

    cout << "所有测试用例通过！约瑟夫问题求解算法实现正确。" << endl;

    return 0;
}