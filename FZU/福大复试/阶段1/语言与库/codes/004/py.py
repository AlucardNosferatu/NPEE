# 题目名称：有效的括号匹配→栈（vector模拟）与unordered_map映射
def is_valid_parentheses(s: str) -> bool:
    # 数据结构1：使用字典建立括号匹配映射关系，对应C++ unordered_map<char, char>
    paren_map = {')': '(', ']': '[', '}': '{'}  # 右括号到左括号的映射，对应unordered_map

    # 数据结构2：使用列表模拟栈（后进先出），对应C++ vector<char>（用push_back/pop_back模拟栈）
    stack = []  # 存储左括号，对应C++ vector<char>作为栈

    # 核心逻辑：遍历字符串，使用栈进行括号匹配，对应string遍历+vector栈操作
    for ch in s:  # 遍历每个字符，对应C++ string的字符遍历
        # 判断条件：当前字符是否为左括号（不在映射的键中），对应STL的find查找
        if ch not in paren_map:  # 左括号，直接入栈，对应STL的find判断键是否存在
            stack.append(ch)  # 左括号入栈，对应vector的push_back
        else:
            # 当前字符为右括号，需要与栈顶左括号匹配，对应STL的empty检查和back访问
            # 边界检查：栈为空或栈顶括号不匹配，则无效
            if not stack or stack[-1] != paren_map[ch]:  # 栈空或不匹配，对应vector的empty和back
                return False  # 匹配失败，返回false，对应C++ bool返回
            # 匹配成功，弹出栈顶左括号，对应vector的pop_back
            stack.pop()  # 弹出栈顶元素，对应vector的pop_back

    # 最终判断：栈为空则所有括号匹配完成，对应vector的empty方法
    return len(stack) == 0  # 栈为空则有效，对应C++的vector::empty()