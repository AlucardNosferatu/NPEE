# noinspection SpellCheckingInspection
def compute_next(pattern):
    """
    【考研/真题标准】next数组生成函数（扩展版：返回结果+手动解题步骤）
    核心规则：
    1. next[0] = -1（固定初始值）
    2. 对i≥1，next[i] = 模式串子串pattern[0..i-1]的最长相等前后缀长度
    3. 双指针法高效计算（和真题手动计算逻辑完全对齐）
    :param pattern: 输入的模式串（如"aabaab"）
    :return: (next_arr, next_steps)
             next_arr：符合真题标准的next数组
             next_steps：list[str]，逐位手动计算步骤（适配考题解析）
    """
    n = len(pattern)
    if n == 0:
        return [], []

    # 初始化next数组，长度和模式串一致
    next_arr = [-1] * n
    # 双指针：j是前缀指针（对应最长前后缀的长度），i是后缀指针（遍历模式串）
    j, i = -1, 0

    # 采集手动解题步骤（核心：逐位解释next[i]的计算逻辑）
    next_steps = [
        "### next数组手动计算步骤（考研真题标准）",
        "| 下标i | pattern[i] | 计算子串（pattern[0..i-1]） | 最长相等前后缀长度 | next[i] | 说明 |",
        "|-------|------------|-----------------------------|--------------------|---------|------|",
        f"| 0     | {pattern[0] if n > 0 else '-'} | 空串                        | -                  | -1      | 考研标准：next[0]固定为-1 |"
    ]

    # 先处理i=0（固定规则）

    # 逐位计算i≥1的next值，并记录步骤
    while i < n - 1:
        if j == -1 or pattern[i] == pattern[j]:
            # 情况1：j=-1（初始/回溯到底） 或 当前字符匹配 → 双指针后移
            i += 1
            j += 1
            next_arr[i] = j
            # 记录当前i的计算步骤
            sub_str = pattern[0:i] if i > 0 else "空串"
            desc = f"子串「{sub_str}」的最长相等前后缀长度为{j}"
            next_steps.append(
                f"| {i}     | {pattern[i]} | {sub_str}                    | {j}                | {j}      | {desc} |")
        else:
            # 情况2：字符不匹配 → 前缀指针回溯到next[j]
            j = next_arr[j]

    return next_arr, next_steps


def compute_nextval(pattern, next_arr):
    """
    完全复刻C语言nextval计算逻辑（扩展版：返回结果+手动解题步骤）
    核心逻辑：while循环递归回溯k，直到k=-1或pattern[i]≠pattern[k]，最终nextval[i]=k
    :param pattern: 目标模式串（str）
    :param next_arr: 首元素为-1的正确next数组（list）
    :return: (nextval_arr, nextval_steps)
             nextval_arr：符合C逻辑的nextval数组
             nextval_steps：list[str]，逐位手动计算步骤（适配考题解析）
    """
    # 边界校验：确保pattern和next数组长度一致
    if len(pattern) != len(next_arr):
        raise ValueError("pattern与next数组长度必须一致！")
    n = len(pattern)
    if n == 0:
        return [], []

    nextval_arr = [-1] * n  # 初始化nextval数组

    # 采集手动解题步骤（核心：逐位解释nextval[i]的递归回溯逻辑）
    nextval_steps = [
        "### nextval数组手动计算步骤（C语言递归回溯逻辑）",
        "| 下标i | pattern[i] | next[i] | k初始值（next[i]） | while循环过程（k的变化） | pattern[i] vs pattern[k] | nextval[i] | 说明 |",
        "|-------|------------|---------|--------------------|-------------------------|--------------------------|------------|------|"
    ]

    for i in range(n):
        if next_arr[i] == -1:
            # C逻辑：next[i]==-1 → nextval[i]=-1
            nextval_arr[i] = -1
            # 记录步骤
            nextval_steps.append(
                f"| {i}     | {pattern[i]} | -1      | -                  | -                       | -                        | -1         | next[i]=-1，直接赋值nextval[i]=-1 |"
            )
        else:
            # C逻辑：k = next[i]
            k = next_arr[i]
            # 记录k的初始值和循环过程
            k_process = [str(k)]  # 记录k的变化轨迹
            compare_result = []  # 记录字符比较结果
            # C逻辑：while (k != -1 && pattern[i] == pattern[k])
            while k != -1 and pattern[i] == pattern[k]:
                prev_k = k
                k = nextval_arr[k]
                k_process.append(str(k))
                compare_result.append(f"pattern[{i}]={pattern[i]} == pattern[{prev_k}]={pattern[prev_k]}")
            # 整理循环过程描述
            k_desc = " → ".join(k_process) if len(k_process) > 1 else k_process[0]
            compare_desc = "；".join(
                compare_result) if compare_result else f"pattern[{i}]={pattern[i]} ≠ pattern[{k}]={pattern[k] if k != -1 else '-'}"
            # 记录步骤
            nextval_arr[i] = k
            nextval_steps.append(
                f"| {i}     | {pattern[i]} | {next_arr[i]}      | {next_arr[i]}              | {k_desc}                | {compare_desc}           | {k}         | 递归回溯至k=-1或字符不相等，赋值nextval[i]={k} |"
            )

    return nextval_arr, nextval_steps


if __name__ == "__main__":
    # 测试模式串：aabaab
    p = "aabaab"
    # 计算next数组+步骤
    next_arr_, next_steps_ = compute_next(p)
    # 计算nextval数组+步骤
    nextval_arr_, nextval_steps_ = compute_nextval(p, next_arr_)

    # 打印结果和步骤
    print("=== next数组结果 ===")
    print(next_arr_)
    print("\n=== next数组解题步骤 ===")
    print("\n".join(next_steps_))

    print("\n=== nextval数组结果 ===")
    print(nextval_arr_)
    print("\n=== nextval数组解题步骤 ===")
    print("\n".join(nextval_steps_))
