import random
import string


def generate_pattern(length=None):
    """生成更易出现长重复前后缀的模式串（长度5-8）"""
    max_length = 8
    min_length = 5
    if length is None:
        length = random.randint(min_length, max_length)  # 固定长度范围5-8
    if length < min_length:
        length = min_length  # 确保足够长度容纳长重复结构

    # 定义基础重复单元（2-3字符，易产生前后缀重复）
    base_units = [
        'ab', 'aa', 'abc', 'aba', 'abba',
        'aaa', 'abab', 'abcab', 'aabbaa'
    ]
    unit = random.choice(base_units)
    unit_len = len(unit)

    # 策略1：通过重复单元生成核心重复结构（例如unit=ab → ababab...）
    pattern = []
    # 先填充2-3个重复单元，确保基础重复结构
    repeat_times = random.randint(2, 3)
    pattern.extend(list(unit * repeat_times))

    # 策略2：递进式复用前缀（在重复单元基础上，追加部分前缀，增强前后缀匹配）
    # 例如当前是abab，追加ab的前1-2个字符 → ababab
    if len(pattern) < length:
        prefix_part = unit[:random.randint(1, unit_len)]  # 取单元的前1-2个字符
        pattern.extend(list(prefix_part))

    # 策略3：若仍不足长度，补充与前缀相关的字符（避免破坏重复结构）
    while len(pattern) < length:
        # 从已有的前缀中随机选1个字符补充（增强关联性）
        prefix_chars = pattern[:min(3, len(pattern))]  # 取前3个字符
        pattern.append(random.choice(prefix_chars))

    # 截断到目标长度（避免超出）
    pattern = pattern[:length]

    # 小概率添加1个不同字符（避免完全重复，增加next数组计算区分度）
    if random.random() < 0.3:  # 30%概率
        last_pos = random.randint(1, length - 1)  # 不在首位置修改
        # 确保修改的字符与原字符不同
        original_char = pattern[last_pos]
        new_char = random.choice(string.ascii_lowercase.replace(original_char, ''))
        pattern[last_pos] = new_char

    return ''.join(pattern)


def compute_next(pattern):
    """修正后：正确计算最长公共前缀后缀长度（不含自身）"""
    n = len(pattern)
    next_arr = [0] * n  # 初始化

    for j in range(1, n):
        max_len = 0
        # 从最大可能长度（j，因为子串长度j+1，前缀最长为j）开始检查，递减效率更高
        for k in range(j, 0, -1):
            # 前缀：pattern[0..k-1]，后缀：pattern[j-k+1..j]
            if pattern[:k] == pattern[j - k + 1: j + 1]:
                max_len = k
                break  # 找到最长的，直接退出
        next_arr[j] = max_len
    return next_arr


def generate_kmp_question():
    pattern_length = random.randint(5, 8)
    pattern = generate_pattern(pattern_length)
    next_arr = compute_next(pattern)

    # 随机选择失配位置i（1到len(pattern)-1，因为j=i-1需>=0）
    mismatch_pos = random.randint(1, len(pattern) - 1)  # 模式串失配位置i
    j = mismatch_pos - 1  # 失配前一个位置j
    jump_target = next_arr[j]  # 跳转位置 = next[j]

    # 构建题目（贴合你的定义）
    question = f"""【KMP算法专项题】（按你的定义）
已知模式串为：{pattern}
1. 请计算该模式串的next数组（next[j]表示以j为结尾的子串的最长公共前缀后缀长度，不含自身）。
2. 若在模式串与主串匹配过程中，模式串指针在位置{mismatch_pos}（0基）处发生失配，
   主串指针不动，模式串指针应跳转至哪个位置（0基）？
"""

    # 构建答案
    answer = f"""【答案】
1. next数组为：{next_arr}
2. 失配后应跳转至位置：{jump_target}
"""

    # 构建解析（按你的定义解释）
    explanation = f"""【解析】
一、next数组计算过程（按你的定义）：
模式串：{pattern}（索引0到{len(pattern) - 1}）
- next[j]表示子串pattern[0..j]的最长公共前缀后缀长度（前缀和后缀均不含子串本身）

"""
    for j in range(len(pattern)):
        substr = pattern[:j + 1]  # 子串pattern[0..j]
        max_len = next_arr[j]
        # 提取前缀和后缀
        prefix = pattern[:max_len] if max_len > 0 else "无"
        suffix = pattern[j - max_len + 1: j + 1] if max_len > 0 else "无"
        explanation += f"- next[{j}]计算：\n"
        explanation += f"  子串：{substr}\n"
        explanation += f"  最长公共前缀后缀长度：{max_len}\n"
        explanation += f"  前缀：{prefix}，后缀：{suffix}\n"
        explanation += f"  故next[{j}] = {max_len}\n"

    # 失配跳转解析
    explanation += f"\n二、失配跳转解析：\n"
    explanation += f"模式串在位置{mismatch_pos}失配，此时前一个位置j = {mismatch_pos} - 1 = {j}\n"
    explanation += f"根据定义，模式串指针应跳转至next[j] = next[{j}] = {next_arr[j]}\n"
    explanation += "（主串指针不动，利用最长公共前缀后缀复用已匹配部分，避免回退）"

    return question, answer, explanation


if __name__ == "__main__":
    q, a, e = generate_kmp_question()
    print("=" * 60)
    print("KMP Algorithm Practice Question (Your Definition)")
    print("=" * 60)
    print(q)

    print("\n" + "=" * 60)
    print("Answer")
    print("=" * 60)
    print(a)

    print("\n" + "=" * 60)
    print("Explanation")
    print("=" * 60)
    print(e)
