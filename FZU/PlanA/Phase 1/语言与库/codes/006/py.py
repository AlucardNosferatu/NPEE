# 题目名称：滑动窗口最大值→deque双端队列维护递减序列，vector存储结果
def max_sliding_window(nums: list[int], k: int) -> list[int]:
    from collections import deque
    
    # 数据结构1：双端队列存储索引，维护递减序列，对应C++ deque<int>
    dq = deque()  # 存储元素索引，对应C++ deque（两端可快速插入删除）
    
    # 数据结构2：列表存储每个窗口的最大值，对应C++ vector<int>
    result = []  # 结果列表，对应C++ vector<int>
    
    # 核心逻辑：遍历数组，维护递减队列
    for i, num in enumerate(nums):  # 遍历数组，对应C++ vector遍历
        # 操作1：移除队列中超出窗口范围的索引（窗口左边界为i-k+1）
        while dq and dq[0] < i - k + 1:  # 检查队首索引是否在窗口内
            dq.popleft()  # 移除队首，对应C++ deque的pop_front
        
        # 操作2：维护递减队列，移除队尾小于当前元素的索引
        while dq and nums[dq[-1]] < num:  # 从队尾开始比较
            dq.pop()  # 移除队尾，对应C++ deque的pop_back
        
        # 操作3：将当前元素索引加入队列
        dq.append(i)  # 加入队尾，对应C++ deque的push_back
        
        # 操作4：当窗口形成时（i>=k-1），记录当前窗口最大值
        if i >= k - 1:  # 窗口已形成
            result.append(nums[dq[0]])  # 队首为当前窗口最大值，对应vector的push_back
    
    return result  # 返回结果列表，对应C++ vector<int>