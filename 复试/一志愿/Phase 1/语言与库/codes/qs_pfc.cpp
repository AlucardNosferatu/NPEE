#include <vector>
#include <cassert>
#include <algorithm> // 用于find函数
using namespace std;

vector<int> qs_pfc(vector<int> input_list)
{
    vector<int> pivot_stack;
    vector<int> ss_stack;
    vector<int> si_stack;
START:
    int seq_size = input_list.size();
    int start_index = 0;
    int pivot_index = seq_size / 2;
    int pivot_element = input_list[pivot_index];
    int i, j;
    int temp;
    bool swap_happened = false;
    goto STATE_1;

STATE_1:
    assert(seq_size == input_list.size() && "STATE_1: seq_size与输入列表长度不一致");
    assert(start_index == 0 && "STATE_1: start_index初始值应为0");
    assert(pivot_index >= 0 && pivot_index < seq_size && "STATE_1: pivot_index超出序列范围");
    assert(find(input_list.begin(), input_list.end(), pivot_element) != input_list.end() && "STATE_1: pivot_element不在输入列表中");
    goto SEARCH_START;

SEARCH_START:
    swap_happened = false;
    i = start_index;
    j = pivot_index + 1;
    goto STATE_2;

STATE_2:
    assert(swap_happened == false && "STATE_2: swap_happened应初始化为false");
    assert(i == start_index && "STATE_2: 左指针i应初始化为start_index");
    assert(j == pivot_index + 1 && "STATE_2: 右指针j应初始化为pivot_index+1");
    assert(i <= pivot_index && "STATE_2: 左指针i初始位置不应超过pivot_index");
    goto SEARCH_I;

SEARCH_I:
    if (i > pivot_index - 1)
        goto SEARCH_J;
    if (input_list[i] > pivot_element)
        goto SEARCH_J;
    else
    {
        i++;
        goto SEARCH_I;
    }

SEARCH_J:
    int right_bound = start_index + seq_size - 1;
    if (j > right_bound)
        goto SWAP_PIJ;
    if (input_list[j] < pivot_element)
        goto SWAP_PIJ;
    else
    {
        j++;
        goto SEARCH_J;
    }

SWAP_PIJ:
    int left_bound = pivot_index - 1;
    right_bound = start_index + seq_size - 1;
    bool i_found = (i <= left_bound) && (input_list[i] > pivot_element);
    bool j_found = (j <= right_bound) && (input_list[j] < pivot_element);
    if (i_found || j_found)
    {
        swap_happened = true;
        if (i_found && j_found)
        {
            temp = input_list[i];
            input_list[i] = input_list[j];
            input_list[j] = temp;
        }
        else if (i_found)
        {
            temp = input_list[i];
            input_list[i] = input_list[pivot_index];
            input_list[pivot_index] = temp;
            pivot_index = i;
            pivot_element = input_list[pivot_index];
        }
        else
        {
            temp = input_list[j];
            input_list[j] = input_list[pivot_index];
            input_list[pivot_index] = temp;
            pivot_index = j;
            pivot_element = input_list[pivot_index];
        }
        goto STATE_3;
    }
    else
    {
        goto STATE_4;
    }

STATE_3:
    assert(swap_happened == true && "STATE_3: 交换后swap_happened应为true");
    assert(pivot_index >= start_index && pivot_index < start_index + seq_size && "STATE_3: 基准点索引超出当前序列范围");
    assert((i <= left_bound || j <= right_bound) && "STATE_3: 交换后指针位置不应同时越界");
    goto SEARCH_START;

STATE_4:
    assert(swap_happened == false && "STATE_4: 未交换时swap_happened应为false");
    assert(!i_found && !j_found && "STATE_4: 无交换时不应存在合法逆序元素");
    assert((i > left_bound || input_list[i] <= pivot_element) && "STATE_4: 左指针i位置元素应≤基准值或越界");
    assert((j > right_bound || input_list[j] >= pivot_element) && "STATE_4: 右指针j位置元素应≥基准值或越界");
    goto DIVIDE_SORT;

DIVIDE_SORT:
    int left_seq_size = pivot_index - start_index;
    if (left_seq_size >= 2)
    {
        ss_stack.push_back(left_seq_size);
        si_stack.push_back(start_index);
        int left_pivot = start_index + (left_seq_size / 2);
        pivot_stack.push_back(left_pivot);
    }
    int right_start = pivot_index + 1;
    int right_seq_size = (start_index + seq_size - 1) - right_start + 1;
    if (right_seq_size >= 2)
    {
        ss_stack.push_back(right_seq_size);
        si_stack.push_back(right_start);
        int right_pivot = right_start + (right_seq_size / 2);
        pivot_stack.push_back(right_pivot);
    }
    goto STATE_5;

STATE_5:
    assert(ss_stack.size() == si_stack.size() && ss_stack.size() == pivot_stack.size() && "STATE_5: 三个栈长度不一致");
    for (int k = 0; k < ss_stack.size(); k++)
    {
        int sub_size = ss_stack[k];
        int sub_start = si_stack[k];
        int sub_pivot = pivot_stack[k];
        assert(sub_size >= 2 && "STATE_5: 栈中子序列长度应≥2");
        assert(sub_start >= 0 && sub_start + sub_size <= input_list.size() && "STATE_5: 子序列超出输入列表范围");
        assert(sub_pivot >= sub_start && sub_pivot < sub_start + sub_size && "STATE_5: 子序列基准点索引非法");
    }
    goto POP_STACK;

POP_STACK:
    if (ss_stack.empty() || si_stack.empty() || pivot_stack.empty())
        goto STATE_7; // 栈空时，跳转至最终状态断言（不再直接return）
    seq_size = ss_stack.back();
    ss_stack.pop_back();
    pivot_index = pivot_stack.back();
    pivot_stack.pop_back();
    start_index = si_stack.back();
    si_stack.pop_back();
    pivot_element = input_list[pivot_index];
    goto STATE_6;

STATE_6:
    assert(seq_size >= 2 && "STATE_6: 处理的子序列长度应≥2");
    assert(start_index >= 0 && start_index + seq_size <= input_list.size() && "STATE_6: 子序列超出输入列表范围");
    assert(pivot_index >= start_index && pivot_index < start_index + seq_size && "STATE_6: 子序列基准点索引非法");
    assert(find(input_list.begin() + start_index, input_list.begin() + start_index + seq_size, pivot_element) != input_list.begin() + start_index + seq_size && "STATE_6: 基准值不在当前子序列中");
    goto SEARCH_START;

// 新增：最终状态断言（即使状态无变化也必须添加），记录算法输出前的最终状态
STATE_7:
    // 断言最终状态：排序结果合法（非空时元素有序、序列长度与输入一致）
    assert(input_list.size() == seq_size && "STATE_7: 输出序列长度与输入不一致");
    for (int k = 1; k < input_list.size(); k++)
    {
        assert(input_list[k] >= input_list[k - 1] && "STATE_7: 输出序列未按升序排序（最终状态非法）");
    }
    goto RETURN_RESULT; // 断言通过后，跳转至专门的return标签

// 新增：专门执行return的动作标签（全大写下划线命名）
RETURN_RESULT:
    return input_list; // 仅执行return，无其他逻辑
}

int main()
{
    vector<int> input_list_ = {7, 3, 5, 2, 8, 4, 1, 6};
    vector<int> sorted_list = qs_pfc(input_list_);
    for (int num : sorted_list)
    {
        printf("%d ", num); // 输出：1 2 3 4 5 6 7 8
    }
    return 0;
}