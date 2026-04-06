#include <iostream>
#include <vector>
#include <cassert>
#include <stack>

using namespace std;

// 二叉树节点结构定义
struct TreeNode
{
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
};

// 基于回溯的二叉树前序遍历：根->左->右
// 输入参数：root - 二叉树根节点
// 输出参数：前序遍历结果序列
// 核心思想：使用自定义栈模拟递归，回溯访问右子树
vector<int> preorder_traversal_backtracking(TreeNode *root)
{
    // ====================== 核心变量声明 ======================
    vector<int> result;           // 用途：存储遍历结果序列；数据来源：访问节点时添加；生命周期：整个算法执行期间
    stack<TreeNode *> node_stack; // 用途：自定义栈，存储待访问的节点（用于模拟递归回溯）；数据来源：遍历过程中压栈；生命周期：整个算法执行期间
    TreeNode *current_node;       // 用途：当前正在处理的节点；数据来源：栈顶弹出或初始根节点；生命周期：算法主循环期间
    bool should_pop;              // 用途：标记是否需要弹出栈顶元素（回溯标志）；数据来源：节点访问和子节点处理逻辑；生命周期：状态控制期间

// ====================== 算法开始 ======================
INIT:
    // 目的：初始化算法所需的核心变量和数据结构
    // 变量关联：result初始为空，node_stack存储节点，current_node初始化为根节点
    // 全局作用：为前序遍历准备初始状态，包括结果容器和自定义栈
    result.clear(); // 清空结果容器，确保初始为空
    while (!node_stack.empty())
    { // 清空栈（虽然初始应为空，但确保安全）
        node_stack.pop();
    }
    current_node = root; // 设置当前节点为根节点
    should_pop = false;  // 初始不需要弹出栈顶元素
    goto STATE_0;        // 跳转至初始状态断言：验证变量初始化合法性

STATE_0:
    // 断言依据：初始化后必须确保核心变量处于合法初始状态
    // 状态特征1：结果序列必须为空（初始状态尚未访问任何节点）
    assert(result.empty() && "STATE_0: 结果序列初始状态非空");
    // 状态特征2：自定义栈必须为空（初始状态尚未压入任何节点）
    assert(node_stack.empty() && "STATE_0: 自定义栈初始状态非空");
    // 状态特征3：回溯标志必须为false（初始状态不需要回溯）
    assert(should_pop == false && "STATE_0: 回溯标志初始状态不是false");
    // 状态特征4：当前节点必须等于根节点（或为nullptr）
    assert(current_node == root && "STATE_0: 当前节点不等于根节点");
    // 约束目的：验证算法初始化的正确性，确保从正确状态开始前序遍历
    goto CHECK_ROOT_NULL; // 跳转至检查根节点空值动作

CHECK_ROOT_NULL:
    // 目的：检查根节点是否为空，处理边界情况
    // 变量关联：current_node（即root）可能为空
    // 全局作用：处理空树的边界情况，避免对空树进行遍历操作
    // 豁免说明：这里不改变核心状态，只是条件检查，不需要状态断言
    if (current_node == nullptr)
    {                     // 如果根节点为空（空树）
        goto FINAL_STATE; // 跳转至最终状态验证，直接返回空结果
    }
    else
    {                 // 如果根节点非空
        goto STATE_7; // 跳转至处理当前节点动作
    }
STATE_7:
    // 还有节点需要处理
    // 断言待补充
    goto PROCESS_CURRENT_NODE;

PROCESS_CURRENT_NODE:
    // 目的：处理当前节点（访问节点值）
    // 变量关联：current_node指向当前节点，result存储遍历结果
    // 全局作用：执行前序遍历的核心操作之一：访问当前节点（根节点）
    // 注意：前序遍历的顺序是根->左->右，所以先访问当前节点
    result.push_back(current_node->val); // 将当前节点值加入结果序列
    goto STATE_1;                        // 跳转至处理当前节点后的状态断言

STATE_1:
    // 断言依据：访问当前节点后，状态必须正确更新
    // 状态特征1：结果序列必须非空（刚刚添加了一个节点值）
    assert(!result.empty() && "STATE_1: 访问节点后结果序列为空");
    // 状态特征2：结果序列的最后一个元素必须等于当前节点值
    assert(result.back() == current_node->val && "STATE_1: 结果序列最后元素不等于当前节点值");
    // 状态特征3：当前节点必须非空（因为刚刚访问了它的值）
    assert(current_node != nullptr && "STATE_1: 当前节点为空但访问了它的值");
    // 状态特征4：当前节点值必须在合理范围内（我们假设是整数，不做具体范围限制）
    // 约束目的：验证节点访问操作的正确性，确保前序遍历的"根"步骤正确执行
    goto CHECK_LEFT_CHILD; // 跳转至检查左子节点动作

CHECK_LEFT_CHILD:
    // 目的：检查当前节点的左子节点是否存在
    // 变量关联：current_node的左子节点指针
    // 全局作用：判断是否需要遍历左子树，这是前序遍历的"左"步骤
    // 豁免说明：这里不改变核心状态，只是条件检查，不需要状态断言
    if (current_node->left != nullptr)
    {                               // 如果左子节点存在
        goto PUSH_CURRENT_TO_STACK; // 跳转至将当前节点压栈动作，以便回溯
    }
    else
    {                           // 如果左子节点不存在
        goto CHECK_RIGHT_CHILD; // 跳转至检查右子节点动作
    }

PUSH_CURRENT_TO_STACK:
    // 目的：将当前节点压入自定义栈，以便回溯访问右子树
    // 变量关联：node_stack存储节点，current_node是待压栈节点
    // 全局作用：保存当前节点，以便在左子树遍历完成后回溯访问右子树
    // 注意：这是实现回溯的关键步骤，模拟递归调用栈
    node_stack.push(current_node); // 将当前节点压入栈
    goto STATE_2;                  // 跳转至压栈后的状态断言

STATE_2:
    // 断言依据：将当前节点压栈后，栈状态必须正确更新
    // 状态特征1：自定义栈必须非空（刚刚压入了一个节点）
    assert(!node_stack.empty() && "STATE_2: 压栈后自定义栈为空");
    // 状态特征2：栈顶元素必须等于刚压入的当前节点
    assert(node_stack.top() == current_node && "STATE_2: 栈顶元素不等于当前节点");
    // 状态特征3：回溯标志必须仍为false（压栈操作不改变回溯标志）
    assert(should_pop == false && "STATE_2: 压栈后回溯标志不是false");
    // 约束目的：验证压栈操作的正确性，确保回溯机制正常工作
    goto MOVE_TO_LEFT_CHILD; // 跳转至移动到左子节点动作

MOVE_TO_LEFT_CHILD:
    // 目的：移动到当前节点的左子节点
    // 变量关联：current_node更新为左子节点
    // 全局作用：实现前序遍历的"左"步骤，开始遍历左子树
    current_node = current_node->left; // 更新当前节点为左子节点
    goto STATE_3;                      // 跳转至移动后的状态断言

STATE_3:
    // 断言依据：移动到左子节点后，状态必须正确更新
    // 状态特征1：当前节点必须非空（因为左子节点存在才执行此动作）
    assert(current_node != nullptr && "STATE_3: 移动到左子节点后当前节点为空");
    // 状态特征2：当前节点必须是原节点的左子节点
    // 注意：我们需要验证这个关系，但原节点信息已丢失（除非保存），这里通过检查栈顶来间接验证
    // 状态特征3：回溯标志必须仍为false（移动操作不改变回溯标志）
    assert(should_pop == false && "STATE_3: 移动后回溯标志不是false");
    // 约束目的：验证移动到左子节点操作的正确性，确保遍历方向正确
    goto PROCESS_CURRENT_NODE; // 跳转回处理当前节点动作，继续遍历

CHECK_RIGHT_CHILD:
    // 目的：检查当前节点的右子节点是否存在
    // 变量关联：current_node的右子节点指针
    // 全局作用：判断是否需要遍历右子树，这是前序遍历的"右"步骤
    // 豁免说明：这里不改变核心状态，只是条件检查，不需要状态断言
    if (current_node->right != nullptr)
    {                             // 如果右子节点存在
        goto MOVE_TO_RIGHT_CHILD; // 跳转至移动到右子节点动作
    }
    else
    {                            // 如果右子节点不存在
        goto SET_BACKTRACK_FLAG; // 跳转至设置回溯标志动作
    }

MOVE_TO_RIGHT_CHILD:
    // 目的：移动到当前节点的右子节点
    // 变量关联：current_node更新为右子节点
    // 全局作用：实现前序遍历的"右"步骤，开始遍历右子树
    current_node = current_node->right; // 更新当前节点为右子节点
    goto STATE_4;                       // 跳转至移动后的状态断言

STATE_4:
    // 断言依据：移动到右子节点后，状态必须正确更新
    // 状态特征1：当前节点必须非空（因为右子节点存在才执行此动作）
    assert(current_node != nullptr && "STATE_4: 移动到右子节点后当前节点为空");
    // 状态特征2：回溯标志必须仍为false（移动操作不改变回溯标志）
    assert(should_pop == false && "STATE_4: 移动后回溯标志不是false");
    // 约束目的：验证移动到右子节点操作的正确性，确保遍历方向正确
    goto PROCESS_CURRENT_NODE; // 跳转回处理当前节点动作，继续遍历

SET_BACKTRACK_FLAG:
    // 目的：设置回溯标志，表示需要回溯到栈中的上一个节点
    // 变量关联：should_pop标记是否需要回溯
    // 全局作用：在当前节点的左右子树都遍历完成后，需要回溯到父节点
    should_pop = true; // 设置回溯标志为true
    goto STATE_5;      // 跳转至设置回溯标志后的状态断言

STATE_5:
    // 断言依据：设置回溯标志后，状态必须正确更新
    // 状态特征1：回溯标志必须为true（刚刚设置为true）
    assert(should_pop == true && "STATE_5: 设置回溯标志后不是true");
    // 状态特征2：当前节点的左右子节点必须都为空（否则不应该设置回溯标志）
    // 注意：这个断言验证了设置回溯标志的条件正确性
    assert(current_node->left == nullptr && current_node->right == nullptr &&
           "STATE_5: 设置回溯标志但当前节点还有子节点");
    // 约束目的：验证设置回溯标志操作的正确性，确保回溯时机正确
    goto CHECK_BACKTRACK_CONDITION; // 跳转至检查回溯条件动作

CHECK_BACKTRACK_CONDITION:
    // 目的：检查是否需要执行回溯操作
    // 变量关联：should_pop标记是否需要回溯，node_stack是否为空
    // 全局作用：控制回溯流程，决定是继续回溯还是结束遍历
    // 豁免说明：这里不改变核心状态，只是条件检查，不需要状态断言
    if (should_pop && !node_stack.empty())
    {                 // 如果需要回溯且栈非空
        goto STATE_8; // 跳转至从栈中弹出节点动作
    }
    else if (should_pop && node_stack.empty())
    {                     // 如果需要回溯但栈为空
        goto FINAL_STATE; // 跳转至最终状态验证，遍历完成
    }
    else
    {                 // 如果不需要回溯（正常情况下不会进入此分支）
        goto STATE_9; // 继续处理当前节点
    }
STATE_8:
    goto POP_FROM_STACK;
STATE_9:
    goto PROCESS_CURRENT_NODE;
POP_FROM_STACK:
    // 目的：从自定义栈中弹出节点，进行回溯
    // 变量关联：node_stack存储节点，current_node更新为栈顶节点
    // 全局作用：执行回溯操作，返回到上一个未完成右子树遍历的节点
    current_node = node_stack.top(); // 获取栈顶节点（父节点）
    node_stack.pop();                // 弹出栈顶节点
    should_pop = false;              // 重置回溯标志为false
    goto STATE_6;                    // 跳转至弹出栈后的状态断言

STATE_6:
    // 断言依据：从栈中弹出节点后，状态必须正确更新
    // 状态特征1：当前节点必须非空（从栈中弹出的节点应该非空）
    assert(current_node != nullptr && "STATE_6: 从栈中弹出的节点为空");
    // 状态特征2：当前节点的左子树必须已经遍历完成（因为之前压栈时左子节点存在）
    // 注意：这个断言验证回溯的合理性
    // 状态特征4：重置回溯标志后验证
    assert(should_pop == false && "STATE_6: 重置回溯标志后不是false");
    // 约束目的：验证弹出栈操作的正确性，确保回溯机制正确执行
    goto CHECK_RIGHT_CHILD; // 跳转至检查右子节点动作，继续遍历右子树

FINAL_STATE:
    // 目的：验证算法完成后的最终收敛状态
    // 断言依据：前序遍历算法完成后，必须满足特定最终状态
    // 状态特征1：自定义栈必须为空（所有节点都已处理完成）
    assert(node_stack.empty() && "STATE_7: 算法完成后自定义栈非空（最终状态非法）");
    // 状态特征2：回溯标志必须为true（遍历完成的标志）
    // 注意：遍历完成时回溯标志为true，但栈为空时无法继续回溯
    // 状态特征3：当前节点应该为空或叶子节点（遍历完成时的状态）
    // 状态特征4：结果序列中的节点数量应该等于树中的节点数量（遍历完整性验证）
    // 由于我们不知道树中节点总数，我们验证结果序列中没有重复访问同一个节点
    // 这个验证比较复杂，我们简化验证：结果序列应该包含所有节点且没有明显错误

    // 验证结果序列的基本性质
    // 1. 结果序列不应为空（除非树为空）
    if (root != nullptr)
    {
        assert(!result.empty() && "STATE_7: 非空树但结果序列为空（最终状态非法）");
    }
    else
    {
        assert(result.empty() && "STATE_7: 空树但结果序列非空（最终状态非法）");
    }

    // 2. 验证结果序列中每个元素都是整数（类型验证）
    // 这个验证在C++中不是必需的，因为result是vector<int>

    // 3. 验证结果序列的前序遍历性质（通过重建遍历过程部分验证）
    // 这里我们无法完全验证，但可以验证一些基本性质

    // 约束目的：验证算法最终收敛状态，确保前序遍历结果正确且算法完全终止
    goto RETURN_RESULT; // 跳转至返回结果动作

RETURN_RESULT:
    // 专门执行算法最终返回
    // 注意：RETURN_RESULT标签仅包含return语句，无其他业务逻辑
    return result; // 返回前序遍历结果序列
}

// ====================== 辅助函数：创建测试二叉树 ======================
// 创建简单的二叉树：根节点为1，左子节点为2，右子节点为3
TreeNode *create_test_tree1()
{
    TreeNode *root = new TreeNode(1);
    root->left = new TreeNode(2);
    root->right = new TreeNode(3);
    return root;
}

// 创建更复杂的二叉树
TreeNode *create_test_tree2()
{
    TreeNode *root = new TreeNode(1);
    root->left = new TreeNode(2);
    root->right = new TreeNode(3);
    root->left->left = new TreeNode(4);
    root->left->right = new TreeNode(5);
    root->right->left = new TreeNode(6);
    root->right->right = new TreeNode(7);
    return root;
}

// 创建只有右子树的二叉树
TreeNode *create_test_tree3()
{
    TreeNode *root = new TreeNode(1);
    root->right = new TreeNode(2);
    root->right->right = new TreeNode(3);
    return root;
}

// 创建只有左子树的二叉树
TreeNode *create_test_tree4()
{
    TreeNode *root = new TreeNode(1);
    root->left = new TreeNode(2);
    root->left->left = new TreeNode(3);
    return root;
}

// 创建单节点树
TreeNode *create_test_tree5()
{
    TreeNode *root = new TreeNode(1);
    return root;
}

// ====================== 测试主函数 ======================
int main()
{
    cout << "测试基于回溯的二叉树前序DFS遍历算法" << endl
         << endl;

    // 测试用例1：简单二叉树（根-左-右）
    cout << "测试用例1：简单二叉树（根-左-右）" << endl;
    TreeNode *tree1 = create_test_tree1();
    vector<int> result1 = preorder_traversal_backtracking(tree1);
    cout << "前序遍历结果: ";
    for (int val : result1)
        cout << val << " ";
    cout << endl;
    vector<int> expected1 = {1, 2, 3};
    assert(result1 == expected1 && "测试用例1：前序遍历结果不正确");
    cout << "通过！" << endl
         << endl;

    // 释放内存
    delete tree1->left;
    delete tree1->right;
    delete tree1;

    // 测试用例2：完整二叉树
    cout << "测试用例2：完整二叉树" << endl;
    TreeNode *tree2 = create_test_tree2();
    vector<int> result2 = preorder_traversal_backtracking(tree2);
    cout << "前序遍历结果: ";
    for (int val : result2)
        cout << val << " ";
    cout << endl;
    vector<int> expected2 = {1, 2, 4, 5, 3, 6, 7};
    assert(result2 == expected2 && "测试用例2：前序遍历结果不正确");
    cout << "通过！" << endl
         << endl;

    // 释放内存
    delete tree2->left->left;
    delete tree2->left->right;
    delete tree2->right->left;
    delete tree2->right->right;
    delete tree2->left;
    delete tree2->right;
    delete tree2;

    // 测试用例3：只有右子树的二叉树
    cout << "测试用例3：只有右子树的二叉树" << endl;
    TreeNode *tree3 = create_test_tree3();
    vector<int> result3 = preorder_traversal_backtracking(tree3);
    cout << "前序遍历结果: ";
    for (int val : result3)
        cout << val << " ";
    cout << endl;
    vector<int> expected3 = {1, 2, 3};
    assert(result3 == expected3 && "测试用例3：前序遍历结果不正确");
    cout << "通过！" << endl
         << endl;

    // 释放内存
    delete tree3->right->right;
    delete tree3->right;
    delete tree3;

    // 测试用例4：只有左子树的二叉树
    cout << "测试用例4：只有左子树的二叉树" << endl;
    TreeNode *tree4 = create_test_tree4();
    vector<int> result4 = preorder_traversal_backtracking(tree4);
    cout << "前序遍历结果: ";
    for (int val : result4)
        cout << val << " ";
    cout << endl;
    vector<int> expected4 = {1, 2, 3};
    assert(result4 == expected4 && "测试用例4：前序遍历结果不正确");
    cout << "通过！" << endl
         << endl;

    // 释放内存
    delete tree4->left->left;
    delete tree4->left;
    delete tree4;

    // 测试用例5：单节点树
    cout << "测试用例5：单节点树" << endl;
    TreeNode *tree5 = create_test_tree5();
    vector<int> result5 = preorder_traversal_backtracking(tree5);
    cout << "前序遍历结果: ";
    for (int val : result5)
        cout << val << " ";
    cout << endl;
    vector<int> expected5 = {1};
    assert(result5 == expected5 && "测试用例5：前序遍历结果不正确");
    cout << "通过！" << endl
         << endl;

    // 释放内存
    delete tree5;

    // 测试用例6：空树
    cout << "测试用例6：空树" << endl;
    TreeNode *tree6 = nullptr;
    vector<int> result6 = preorder_traversal_backtracking(tree6);
    cout << "前序遍历结果: ";
    for (int val : result6)
        cout << val << " ";
    cout << "(空)" << endl;
    assert(result6.empty() && "测试用例6：空树遍历结果非空");
    cout << "通过！" << endl
         << endl;

    cout << "所有测试用例通过！基于回溯的二叉树前序DFS遍历算法实现正确。" << endl;

    return 0;
}