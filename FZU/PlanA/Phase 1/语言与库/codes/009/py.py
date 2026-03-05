# 题目名称：两个数组的交集II→unordered_map频次统计，vector动态添加结果
def intersect(nums1: list[int], nums2: list[int]) -> list[int]:
    # 数据结构定义：使用字典统计nums1中元素频次，对应C++ unordered_map<int, int>
    freq_map = {}  # 键：元素值，值：出现次数，对应C++ unordered_map
    
    # 核心逻辑1：遍历nums1统计每个元素的出现频次
    for num in nums1:  # 遍历第一个数组，对应C++ vector遍历
        freq_map[num] = freq_map.get(num, 0) + 1  # 更新频次，对应unordered_map的[]运算符
    
    # 数据结构定义：列表存储交集结果，对应C++ vector<int>
    result = []  # 存储交集元素，对应C++ vector
    
    # 核心逻辑2：遍历nums2查找共同元素（考虑频次）
    for num in nums2:  # 遍历第二个数组，对应C++ vector遍历
        # 判断条件：元素在频次字典中且剩余频次大于0
        if num in freq_map and freq_map[num] > 0:  # 对应unordered_map的find查找和值比较
            result.append(num)  # 将元素加入结果列表，对应vector的push_back
            freq_map[num] -= 1  # 减少对应元素的剩余频次，对应unordered_map的值修改
    
    # 返回结果：交集元素列表（考虑频次），对应C++ vector<int>
    return result