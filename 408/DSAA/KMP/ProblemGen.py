import random
import string

from KMP4PG import compute_next, compute_nextval


def generate_kmp_pattern(
        min_len: int = 5,
        max_len: int = 8,
        core_chars_num: int = 2,  # 核心重复字符数（2-3个最佳）
        retry_times: int = 10  # 无效模式串重试次数
):
    """
    生成适配KMP考题的随机模式串（考研真题风格）
    :param min_len: 模式串最小长度（默认5）
    :param max_len: 模式串最大长度（默认8）
    :param core_chars_num: 核心重复字符数（2-3个，保证前后缀可计算）
    :param retry_times: 生成无效模式串时的重试次数
    :return: 符合考题要求的模式串（None表示重试上限）
    """
    # 1. 基础配置：小写字母字符集，长度范围
    chars = string.ascii_lowercase
    length = random.randint(min_len, max_len)

    # 2. 重试机制：确保生成的模式串有考察价值
    # noinspection SpellCheckingInspection
    for _ in range(retry_times):
        # 2.1 选核心字符（保证重复度）
        core_chars = random.sample(chars, core_chars_num)
        pattern = []

        # 2.2 构建模式串：核心字符占比60%+，随机字符占比40%-
        for idx in range(length):
            # 核心位置（0/2/4...）填充核心字符，其余填充随机字符
            if idx % 3 == 0:
                pattern.append(random.choice(core_chars))
            else:
                # 随机字符中也可能包含核心字符，增加随机性
                pattern.append(random.choice(chars))

        # 2.3 转为字符串
        pattern_str = ''.join(pattern)

        # 2.4 验证有效性：排除极端情况
        next_arr, _ = compute_next(pattern_str)
        # 有效条件1：不是全相同字符（如"aaaaa"，next数组无考察意义）
        all_same = len(set(pattern_str)) == 1
        # 有效条件2：不是全不同字符（如"abcde"，next数组除-1外全0）
        all_diff = len(set(pattern_str)) == length
        # 有效条件3：存在非0的next值（保证有考察点）
        has_non_zero_next = any(v != 0 and v != -1 for v in next_arr)

        # 满足所有有效条件则返回
        if not all_same and not all_diff and has_non_zero_next:
            return pattern_str

    # 重试上限仍未生成有效串
    return None


# ==================== 测试生成器 ====================
if __name__ == "__main__":
    # 生成5个测试用模式串
    print("【KMP考题模式串生成测试】")
    for i in range(5):
        p = generate_kmp_pattern()
        if p:
            next_arr_, _ = compute_next(p)
            nextval_arr, _ = compute_nextval(p, next_arr_)
            print(f"第{i + 1}个模式串：{p}\n对应的next数组：{next_arr_}\n对应的nextval数组：{nextval_arr}")
        else:
            print(f"第{i + 1}个模式串：生成失败（重试上限）")
