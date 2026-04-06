# 题目名称：下一个更大元素I→unordered_map映射+vector存储结果，stack单调栈辅助
def next_greater_element(nums1: list[int], nums2: list[int]) -> list[int]:
    # 数据结构1：使用字典存储nums2中每个元素的下一个更大元素，对应C++ unordered_map<int, int>
    next_greater_map = {}  # 键：nums2元素，值：下一个更大元素，对应C++ unordered_map
    
    # 数据结构2：使用列表模拟单调栈（递减栈），对应C++ vector<int>（用push_back/pop_back模拟栈）
    stack = []  # 存储尚未找到下一个更大元素的元素索引，对应C++ vector<int>
    
    # 核心逻辑：遍历nums2，利用单调栈建立每个元素的下一个更大元素映射
    for num in nums2:  # 遍历第二个数组，对应C++ vector遍历
        # 判断条件：当栈不为空且当前元素大于栈顶元素时，说明找到栈顶元素的下一个更大元素
        while stack and stack[-1] < num:  # 栈顶元素小于当前元素，对应vector的back访问和比较
            smaller = stack.pop()  # 弹出栈顶元素，对应vector的pop_back
            next_greater_map[smaller] = num  # 建立映射关系，对应unordered_map的[]赋值
        
        # 将当前元素入栈，等待找到它的下一个更大元素
        stack.append(num)  # 当前元素入栈，对应vector的push_back
    
    # 处理栈中剩余元素：它们没有下一个更大元素，映射为-1
    while stack:  # 栈不为空，对应vector的empty检查
        remaining = stack.pop()  # 弹出元素，对应vector的pop_back
        next_greater_map[remaining] = -1  # 设置默认值-1，对应unordered_map的[]赋值
    
    # 数据结构3：列表存储nums1中每个元素对应的结果，对应C++ vector<int>
    result = []  # 结果列表，对应C++ vector<int>
    
    # 核心逻辑2：遍历nums1，从映射表中查找结果
    for num in nums1:  # 遍历第一个数组（子集），对应C++ vector遍历
        result.append(next_greater_map[num])  # 查找映射并添加到结果，对应unordered_map的查找和vector的push_back
    
    return result  # 返回结果列表，对应C++ vector<int>