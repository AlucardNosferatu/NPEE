# 题目名称：和为K的子数组个数统计→unordered_map前缀和统计，int变量计数
def subarray_sum_equals_k(nums: list[int], k: int) -> int:
    # 数据结构定义：使用字典存储前缀和出现的次数，对应C++ unordered_map<int, int>
    prefix_sum_map = {}  # 键：前缀和，值：该前缀和出现的次数，对应C++ unordered_map
    prefix_sum_map[0] = 1  # 初始化前缀和为0的次数为1，对应空子数组的情况
    
    current_sum = 0  # 当前前缀和，对应C++ int
    count = 0  # 满足条件的子数组个数，对应C++ int
    
    # 核心逻辑：遍历数组，计算前缀和，查找满足条件的子数组
    for num in nums:  # 遍历数组元素，对应C++ vector遍历
        current_sum += num  # 更新当前前缀和，对应C++累加
        
        # 判断条件：查找是否存在前缀和等于current_sum - k
        # 如果存在，说明从该前缀和的位置到当前位置的子数组和为k
        target = current_sum - k  # 需要查找的目标前缀和，对应C++ int
        if target in prefix_sum_map:  # 查找目标前缀和是否存在，对应STL的find方法
            count += prefix_sum_map[target]  # 增加计数，对应unordered_map的值访问
        
        # 核心操作：将当前前缀和加入映射表（更新出现次数）
        prefix_sum_map[current_sum] = prefix_sum_map.get(current_sum, 0) + 1
        # 对应C++ unordered_map的[]运算符（若键不存在则插入默认值0再加1）
    
    return count  # 返回结果计数，对应C++ int类型