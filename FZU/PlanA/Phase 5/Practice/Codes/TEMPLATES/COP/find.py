from cop import NoApplicableAlgorithm, AlgorithmChain, AlgorithmUnit, NotApplicable


# 假设 AlgorithmChain、AlgorithmUnit、NotApplicable、NoApplicableAlgorithm 已定义（与之前一致）

# ---------- 查找算法实现（接受字典输入） ----------
def linear_search(inputs):
    """线性查找，兜底算法"""
    data = inputs["data"]
    target = inputs["target"]
    for i, val in enumerate(data):
        if val == target:
            return i
    return -1


def binary_search(inputs):
    """二分查找，要求数据有序"""
    data = inputs["data"]
    target = inputs["target"]
    # 运行时验证有序性
    if not all(data[i] <= data[i + 1] for i in range(len(data) - 1)):
        raise NotApplicable("数据并非真正有序")
    left, right = 0, len(data) - 1
    while left <= right:
        mid = (left + right) // 2
        if data[mid] == target:
            return mid
        elif data[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


def hash_search(inputs):
    """哈希查找，利用集合快速判断存在性"""
    data = inputs["data"]
    target = inputs["target"]
    s = set(data)
    if target in s:
        for i, val in enumerate(data):
            if val == target:
                return i
    return -1


def zero_array_search(inputs):
    """特例：如果数组全为零，查找0直接返回0，否则返回-1"""
    data = inputs["data"]
    target = inputs["target"]
    if all(v == 0 for v in data):
        if target == 0:
            return 0
        else:
            return -1
    raise NotApplicable("数组不全为零，不适用此特例")


# ---------- 前置条件函数（接受字典输入） ----------
def pre_binary(inputs):
    data = inputs["data"]
    return len(data) > 0 and all(data[i] <= data[i + 1] for i in range(len(data) - 1))


def pre_hash(inputs):
    data = inputs["data"]
    return len(data) < 10000  # 假设数据量小于10000才用哈希


def pre_zero(inputs):
    data = inputs["data"]
    return len(data) > 0 and data[0] == 0 and data[-1] == 0  # 粗略判断


def pre_linear(inputs):
    _ = inputs
    return True  # 总是适用


# ---------- 后置条件：验证结果正确性 ----------
def post_check(inputs, result):
    data = inputs["data"]
    target = inputs["target"]
    if result == -1:
        return target not in data
    else:
        return 0 <= result < len(data) and data[result] == target


# ---------- 组装算法链 ----------
algorithms = [
    AlgorithmUnit(zero_array_search, pre_condition=pre_zero, post_condition=post_check, name="ZeroSpecial"),
    AlgorithmUnit(binary_search, pre_condition=pre_binary, post_condition=post_check, name="Binary"),
    AlgorithmUnit(hash_search, pre_condition=pre_hash, post_condition=post_check, name="Hash"),
    AlgorithmUnit(linear_search, pre_condition=pre_linear, post_condition=post_check, name="Linear")
]

chain = AlgorithmChain(algorithms)

# ---------- 测试用例 ----------
test_cases = [
    ([1, 2, 3, 4, 5], 3, "有序数组，查找存在"),
    ([5, 4, 3, 2, 1], 3, "无序数组，查找存在"),
    ([0, 0, 0, 0], 0, "全零数组，查找0"),
    ([0, 0, 0, 0], 1, "全零数组，查找非0"),
    ([1, 3, 5, 7], 4, "有序数组，查找不存在"),
    ([1, 2, 3, 4, 5] * 2000, 3, "大数据集，触发哈希前置条件"),
]

for data_, target_, desc in test_cases:
    print(f"\n=== {desc} ===")
    inputs_ = {"data": data_, "target": target_}
    try:
        result_ = chain.run(inputs_)
        print(f"结果索引: {result_}")
    except NoApplicableAlgorithm as e:
        print(f"错误: {e}")
    except Exception as e:
        print(f"异常: {e}")
