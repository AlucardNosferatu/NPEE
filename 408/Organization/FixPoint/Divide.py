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


if __name__ == '__main__':
    a = -64
    b = 7
    if a * b > 0:
        sign = 1
    else:
        sign = -1
    a = abs(a)
    b = abs(b)
    q_bin = []
    a_bin = int_to_binary(a)
    r_bin = '00000000'
    for i in range(9):
        r = binary_to_int(r_bin)
        r -= b
        if r < 0:
            q_bin.append('0')
            r += b
        else:
            q_bin.append('1')
        r_bin = int_to_binary(r)
        r_a_bin = (r_bin + a_bin + '0')[1:]
        r_bin = r_a_bin[:8]
        a_bin = r_a_bin[8:]
    q_bin = ''.join(q_bin)[1:]
    q = sign * binary_to_int(q_bin)
    print(q)
