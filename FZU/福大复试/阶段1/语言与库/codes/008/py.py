# 题目名称：最长连续序列→unordered_set去重与查找，vector初始化转换
def longest_consecutive_sequence(nums: list[int]) -> int:
    # 数据结构定义：使用集合存储所有数字实现O(1)查找，对应C++ unordered_set<int>
    num_set = set(nums)  # 去重并建立查找表，对应C++ unordered_set<int>
    
    longest_streak = 0  # 记录最长连续序列长度，对应C++ int
    
    # 核心逻辑：遍历集合，查找连续序列的起点
    for num in num_set:  # 遍历集合元素，对应C++ unordered_set迭代器遍历
        # 判断条件：当前数字是否为连续序列的起点（即前一个数字不在集合中）
        if num - 1 not in num_set:  # 检查前驱是否存在，对应STL的find方法
            current_num = num  # 当前连续序列的起点
            current_streak = 1  # 当前连续序列长度
            
            # 核心操作：从起点开始向后查找连续数字
            while current_num + 1 in num_set:  # 检查后继是否存在，对应STL的find方法
                current_num += 1  # 移动到下一个连续数字
                current_streak += 1  # 序列长度增加
            
            # 更新最长连续序列长度，对应C++ max函数
            longest_streak = max(longest_streak, current_streak)
    
    return longest_streak  # 返回结果，对应C++ int类型