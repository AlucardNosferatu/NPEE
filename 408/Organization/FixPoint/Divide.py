import random


def int_to_binary(num: int) -> str:
    """
    将整数转换为8位二进制带符号数的字符串表示。

    参数:
        num (int): 需要转换的整数

    返回:
        str: 8位二进制带符号数的字符串，例如 "00001000"

    异常:
        ValueError: 如果输入的整数超出了8位带符号数的表示范围（-128到127）
    """
    if num < -128 or num > 127:
        raise ValueError("输入的整数超出了8位带符号数的表示范围")

    # 处理负数的情况
    if num < 0:
        # 计算补码
        num = (1 << 8) + num

    # 转换为二进制字符串并去掉前缀 '0b'
    binary_str = bin(num)[2:]

    # 确保字符串长度为8位，不足时在左边补0
    return binary_str.zfill(8)


def binary_to_int(binary_str: str) -> int:
    """
    将8位二进制带符号数字符串转换为对应的整数。

    参数:
        binary_str (str): 8位二进制带符号数字符串，例如 "00001000"

    返回:
        int: 对应的整数值

    异常:
        ValueError: 如果输入字符串长度不是8位或包含非二进制字符
    """
    # 验证输入字符串是否为有效的8位二进制
    if len(binary_str) != 8 or not all(c in '01' for c in binary_str):
        raise ValueError("输入必须是8位二进制字符串")

    # 检查符号位
    if binary_str[0] == '0':
        # 正数：直接转换为整数
        return int(binary_str, 2)
    else:
        # 负数：计算补码对应的绝对值，再取负
        # 方法1：使用位运算
        value = int(binary_str, 2)
        return value - (1 << 8)

        # 方法2：手动计算补码
        # inverted_str = ''.join('1' if c == '0' else '0' for c in binary_str[1:])
        # absolute_value = int(inverted_str, 2) + 1
        # return -absolute_value


def resume_remainder(a, b):
    sign = get_q_sign(a, b)
    a_bin, b, q_bin, r_bin = init_remainder(a, b)
    # 初始化信息记录
    info_log = [
        f"初始化参数 | a绝对值二进制: {a_bin}, 除数b: {b}",
        f"初始余数r_bin: {r_bin}, 商寄存器q_bin: {q_bin}"
    ]

    for i in range(9):
        info_log.append(f"\n-- 第{i}次迭代 --")
        r = tentative_divisor_sub(b, q_bin, r_bin)
        # 记录试探减法结果
        if r < 0:
            info_log.append(f"试探减法结果r={r} < 0 -> 商位设为0，恢复余数: {r}+{b}={r + b}")
        else:
            info_log.append(f"试探减法结果r={r} >= 0 -> 商位设为1")

        r_bin, a_bin = left_shift_remainder(a_bin, r)
        # 记录左移操作结果
        info_log.append(f"左移后余数r_bin: {r_bin} | 被除数a_bin: {a_bin}")
        # 记录当前商状态
        info_log.append(f"当前商q_bin: {''.join(q_bin)}")

    q_bin_str = ''.join(q_bin)[1:]  # 移除首位符号位
    q = sign * binary_to_int(q_bin_str)
    # 最终结果记录
    info_log.append(f"\n最终商: {q} (二进制: {q_bin_str})")
    return q, "\n".join(info_log)


def left_shift_remainder(a_bin, r):
    r_bin = int_to_binary(r)
    r_a_bin = (r_bin + a_bin + '0')[1:]
    r_bin = r_a_bin[:8]
    a_bin = r_a_bin[8:]
    return r_bin, a_bin


def tentative_divisor_sub(b, q_bin, r_bin):
    r = binary_to_int(r_bin)
    r -= b
    if r < 0:
        q_bin.append('0')
        r += b
    else:
        q_bin.append('1')
    return r


def init_remainder(a, b):
    a = abs(a)
    b = abs(b)
    q_bin = []
    a_bin = int_to_binary(a)
    r_bin = '00000000'
    return a_bin, b, q_bin, r_bin


def get_q_sign(a, b):
    if a * b > 0:
        sign = 1
    else:
        sign = -1
    return sign


def generate_8bit_division():
    while True:
        # 生成有效除数范围
        if random.choice([True, False]):
            divisor = random.randint(1, 31)  # 正数范围
        else:
            divisor = random.randint(-32, -1)  # 负数范围

        # 计算被除数范围
        if divisor > 0:
            min_dividend = 4 * divisor
            max_dividend = 127
        else:
            min_dividend = -128
            max_dividend = 4 * divisor  # 负数乘法产生更小值

        # 生成被除数并验证范围有效性
        if min_dividend > max_dividend:
            continue  # 数学上不可能触发，防御性代码

        dividend = random.randint(min_dividend, max_dividend)

        # 最终验证（防御性检查）
        if dividend // divisor >= 4:
            return dividend, divisor


if __name__ == '__main__':
    dividend, divisor = generate_8bit_division()
    print(f"被除数: {dividend}（4位二进制：{format(dividend & 0b11111111, '08b')}）")
    print(f"除数: {divisor}（4位二进制：{format(divisor & 0b11111111, '08b')}）")
    print(f"验证商：{dividend // divisor}")
    q_, log = resume_remainder(dividend, divisor)
    print(f"答案商：{q_}")
    print(f"过程：{log}")
