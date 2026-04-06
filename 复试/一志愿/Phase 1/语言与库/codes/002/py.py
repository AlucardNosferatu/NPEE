# 题目名称：区间合并→vector排序与双指针，pair存储区间端点
def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    # 数据结构定义：使用列表存储合并后的结果区间，对应C++ vector<pair<int,int>>或vector<vector<int>>
    merged = []  # 结果列表，每个元素为区间[start,end]，对应C++ vector

    # 核心逻辑1：按区间起点进行排序，对应STL的sort算法（自定义比较器）
    sorted_intervals = sorted(intervals, key=lambda x: x[0])  # 按第一元素升序排序，对应STL sort

    # 核心逻辑2：遍历排序后的区间，合并重叠区间，对应vector迭代遍历
    for interval in sorted_intervals:
        # 操作目的：获取当前区间的起止点，对应C++ pair的first/second或vector元素访问
        start, end = interval[0], interval[1]  # 解构赋值，对应STL的pair或tuple

        # 判断条件：检查结果列表为空或当前区间与前一区间不重叠，对应vector的back操作
        if not merged or merged[-1][1] < start:  # 无重叠，对应STL的vector::back()访问
            # 核心操作：将当前区间加入结果列表，对应STL的push_back
            merged.append([start, end])  # 添加新区间，对应vector的push_back
        else:
            # 核心操作：合并重叠区间，更新前一区间的结束点，对应STL的修改操作
            merged[-1][1] = max(merged[-1][1], end)  # 扩展区间结束点，对应修改pair的second

    # 返回结果：合并后的区间列表，对应C++ vector<vector<int>>或vector<pair<int,int>>
    return merged