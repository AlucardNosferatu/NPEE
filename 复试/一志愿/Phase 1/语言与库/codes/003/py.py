# 题目名称：前K个高频元素统计→unordered_map频次统计+vector自定义排序
def top_k_frequent(nums: list[int], k: int) -> list[int]:
    # 数据结构1：使用字典统计元素出现频次，对应C++ unordered_map<int, int>
    freq_map = {}  # 键：元素值，值：出现次数，对应C++ unordered_map
    for num in nums:  # 遍历统计，对应STL的[]运算符频次更新
        freq_map[num] = freq_map.get(num, 0) + 1  # 更新频次，对应unordered_map的find/insert

    # 数据结构2：将字典项转换为列表，每个项为(元素,频次)，对应C++ vector<pair<int,int>>
    items = list(freq_map.items())  # 转换为(元素,频次)列表，对应vector<pair<int,int>>

    # 核心逻辑：按频次降序排序，对应STL sort算法+自定义比较函数
    # 使用lambda指定按第二元素（频次）降序排列，对应STL的比较器
    sorted_items = sorted(items, key=lambda x: -x[1])  # 降序排序，对应sort+greater或自定义比较

    # 结果提取：获取前k个高频元素，对应vector的迭代器或下标访问
    result = []
    for i in range(min(k, len(sorted_items))):  # 防止k超出范围，对应STL的size检查
        result.append(sorted_items[i][0])  # 提取元素值，对应vector的push_back

    return result  # 返回结果列表，对应C++ vector<int>