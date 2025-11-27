# noinspection SpellCheckingInspection
def compute_next(pattern):
    """
    【考研/真题标准】next数组生成函数
    核心规则：
    1. next[0] = -1（固定初始值）
    2. 对i≥1，next[i] = 模式串子串pattern[0..i-1]的最长相等前后缀长度
    3. 双指针法高效计算（和真题手动计算逻辑完全对齐）
    :param pattern: 输入的模式串（如"aabaab"）
    :return: 符合真题标准的next数组
    """
    n = len(pattern)
    if n == 0:
        return []

    # 初始化next数组，长度和模式串一致
    next_arr = [-1] * n
    # 双指针：j是前缀指针（对应最长前后缀的长度），i是后缀指针（遍历模式串）
    j, i = -1, 0

    while i < n - 1:  # i最多到n-2，因为要算next[i+1]
        if j == -1 or pattern[i] == pattern[j]:
            # 情况1：j=-1（初始/回溯到底） 或 当前字符匹配 → 双指针后移
            i += 1
            j += 1
            next_arr[i] = j  # next[i] = 最长相等前后缀长度j
        else:
            # 情况2：字符不匹配 → 前缀指针回溯到next[j]
            j = next_arr[j]

    return next_arr


def compute_nextval(pattern, next_arr):
    """
    完全复刻你提供的C语言nextval计算逻辑
    核心逻辑：while循环递归回溯k，直到k=-1或pattern[i]≠pattern[k]，最终nextval[i]=k
    :param pattern: 目标模式串（str）
    :param next_arr: 首元素为-1的正确next数组（list）
    :return: 符合该逻辑的nextval数组（list）
    """
    # 边界校验：确保pattern和next数组长度一致
    if len(pattern) != len(next_arr):
        raise ValueError("pattern与next数组长度必须一致！")
    n = len(pattern)
    if n == 0:
        return []

    nextval_arr = [-1] * n  # 初始化nextval数组

    for i in range(n):
        if next_arr[i] == -1:
            # C逻辑：next[i]==-1 → nextval[i]=-1
            nextval_arr[i] = -1
        else:
            # C逻辑：k = next[i]
            k = next_arr[i]
            # C逻辑：while (k != -1 && pattern[i] == pattern[k])
            while k != -1 and pattern[i] == pattern[k]:
                # C逻辑：k = nextval[k]（向前继续跳）
                k = nextval_arr[k]
            # C逻辑：nextval[i] = k
            nextval_arr[i] = k

    return nextval_arr


# ==================== 验证：真题高频示例 ====================
# noinspection SpellCheckingInspection
if __name__ == "__main__":
    # 示例1：2024真题模式串"aabaab"
    # noinspection SpellCheckingInspection
    pattern1 = "abcaabbcabcaabdab"
    next1 = compute_next(pattern1)
    print(f"模式串：{pattern1}")
    print(f"next数组：{next1}")  # 预期输出：[-1, 0, 1, 0, 1, 2]（完全匹配真题）

    # 调用函数计算nextval
    nv1 = compute_nextval(pattern1, next1)

    # 输出结果（验证是否与真题一致）
    print(f"模式串：{pattern1}")
    print(f"输入next数组：{next1}")
    print(f"计算得到nextval数组：{nv1}")  # 预期输出：[-1, -1, 1, -1, -1, 1]
