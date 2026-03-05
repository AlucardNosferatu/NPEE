# 题目名称：两数之和索引查找→unordered_map映射，vector存储
def two_sum_indices(nums: list[int], target: int) -> list[int]:
    # 数据结构定义：使用字典存储“数值->索引”映射，对应C++ unordered_map<int, int>
    index_map = {}  # 键：数组元素值，值：该元素索引，对应C++ unordered_map

    # 核心逻辑：遍历数组，利用哈希表实现O(1)查找互补数
    for i, num in enumerate(nums):
        complement = target - num

        # 判断条件：查找互补数是否已在映射表中，对应STL的find方法检查是否存在键
        if complement in index_map:  # 查找键是否存在，对应STL的find方法或count方法
            # 返回结果：找到匹配对，返回两个索引，对应C++ vector的初始化或push_back
            return [index_map[complement], i]  # 结果列表，对应C++ vector<int>

        # 核心操作：将当前数及其索引加入映射表，对应STL的insert方法或[]运算符赋值
        index_map[num] = i  # 新增/更新键值对（值：索引），对应STL的[]运算符

    # 边界处理：若无解，返回空列表（题目通常保证有解，此处为防御性代码），对应C++空vector
    return []  # 空结果列表，对应C++ vector<int>()