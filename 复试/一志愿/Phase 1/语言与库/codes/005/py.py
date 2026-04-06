# 题目名称：分发饼干→vector排序与贪心双指针
def assign_cookies(g: list[int], s: list[int]) -> int:
    # 数据结构定义：使用列表存储孩子的胃口值和饼干尺寸，对应C++ vector<int>
    # 对两个列表进行排序，以便使用贪心策略，对应STL sort算法
    g.sort()  # 孩子胃口值升序排序，对应C++ sort(g.begin(), g.end())
    s.sort()  # 饼干尺寸升序排序，对应C++ sort(s.begin(), s.end())

    # 核心逻辑：贪心策略，用最小尺寸饼干满足最小胃口孩子
    child_idx = 0  # 当前孩子索引，对应C++ int
    cookie_idx = 0  # 当前饼干索引，对应C++ int
    
    # 双指针遍历，直到孩子或饼干用完，对应vector的size检查
    while child_idx < len(g) and cookie_idx < len(s):
        # 判断条件：当前饼干能否满足当前孩子，对应vector下标访问
        if s[cookie_idx] >= g[child_idx]:  # 可以满足，对应C++比较操作
            child_idx += 1  # 孩子被满足，移动到下一个孩子
        # 无论是否满足，饼干都会被考虑（不满足则换更大饼干）
        cookie_idx += 1  # 移动到下一块饼干

    # 返回结果：被满足的孩子数量，对应C++ int类型
    return child_idx