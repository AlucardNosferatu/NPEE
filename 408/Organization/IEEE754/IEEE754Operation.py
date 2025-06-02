import random


def generate_float():
    """生成符合条件的随机浮点数"""
    # 生成整数部分 (-500 到 500 之间)
    integer_part = random.randint(-500, 500)

    # 生成小数部分 (最多3个2的负幂之和，指数范围从-1到-4)
    exponents = list(range(-1, -5, -1))  # [-1, -2, -3, -4]
    random.shuffle(exponents)
    # 随机选择1到3个不同的指数
    num_exponents = random.randint(1, 3)
    selected_exponents = exponents[:num_exponents]

    # 计算小数部分
    fractional_part = sum(2 ** exp for exp in selected_exponents)

    # 合并整数和小数部分
    return integer_part + fractional_part


def float_to_ieee754(num):
    import struct
    # 处理特殊情况：零
    if num == 0.0:
        return '0', '00000000', '00000000000000000000000'

    # 获取符号位
    sign = '0' if num >= 0 else '1'
    num = abs(num)

    # 将浮点数转换为32位二进制表示
    packed = struct.pack('!f', num)
    bits = ''.join(f'{byte:08b}' for byte in packed)

    # 提取符号、指数和尾数部分
    exponent_bits = bits[1:9]
    mantissa_bits = bits[9:]

    # 转换为二进制字符串
    return sign, exponent_bits, mantissa_bits


def ieee754_to_float(sign_bit, exponent_bits, mantissa_bits):
    # 计算符号部分
    sign = -1 if sign_bit == '1' else 1

    # 计算指数部分（减去偏置值127）
    exponent = int(exponent_bits, 2) - 127

    # 计算尾数部分（加上隐含的1）
    mantissa = 1.0
    for i, bit in enumerate(mantissa_bits):
        if bit == '1':
            mantissa += 2 ** -(i + 1)

    # 计算最终的浮点数
    result = sign * (2 ** exponent) * mantissa

    # 处理特殊情况：零
    if exponent_bits == '00000000' and mantissa_bits == '00000000000000000000000':
        return 0.0

    return result


def ieee754_operation(op, num1, num2):
    s1, e1, m1 = num1
    s2, e2, m2 = num2

    # 转换阶码为整数
    E1 = int(e1, 2) - 127
    E2 = int(e2, 2) - 127

    # 转换尾数为带隐含位的小数
    M1 = 1.0 + int(m1, 2) / (2 ** 23)
    M2 = 1.0 + int(m2, 2) / (2 ** 23)

    # 符号处理
    sign1 = -1 if s1 == '1' else 1
    sign2 = -1 if s2 == '1' else 1

    # 对阶：调整较小的指数
    if E1 > E2:
        delta_E = E1 - E2
        M2 = M2 / (2 ** delta_E)
        E2 = E1
    elif E2 > E1:
        delta_E = E2 - E1
        M1 = M1 / (2 ** delta_E)
        E1 = E2

    # 尾数加减
    if op == '+':
        M_sum = sign1 * M1 + sign2 * M2
    elif op == '-':
        M_sum = sign1 * M1 - sign2 * M2
    else:
        raise ValueError("Unsupported operation")

    # 规格化处理
    sign_result = 1 if M_sum >= 0 else -1
    M_sum_abs = abs(M_sum)

    # 规格化：调整到1.0 <= M < 2.0
    E_result = E1
    while M_sum_abs >= 2.0:
        M_sum_abs /= 2.0
        E_result += 1
    while M_sum_abs < 1.0 and M_sum_abs != 0:
        M_sum_abs *= 2.0
        E_result -= 1

    # 特殊情况处理：零值
    if M_sum_abs == 0:
        return '0', '00000000', '00000000000000000000000'

    # 提取尾数（去掉隐含位）
    fraction = M_sum_abs - 1.0
    mantissa = int(fraction * (2 ** 23))
    mantissa_bin = format(mantissa, '023b')

    # 计算阶码（加上偏移量）
    exponent = E_result + 127
    exponent_bin = format(exponent, '08b')

    # 符号位
    sign_bin = '1' if sign_result == -1 else '0'

    return sign_bin, exponent_bin, mantissa_bin


if __name__ == '__main__':
    a = generate_float()
    b = generate_float()
    print(a, b)
    a_ieee754 = float_to_ieee754(a)
    b_ieee754 = float_to_ieee754(b)
    sign, exp, man = ieee754_operation('+', a_ieee754, b_ieee754)
    print(ieee754_to_float(sign_bit=sign, exponent_bits=exp, mantissa_bits=man))
    print(a + b)
    sign, exp, man = ieee754_operation('-', a_ieee754, b_ieee754)
    print(ieee754_to_float(sign_bit=sign, exponent_bits=exp, mantissa_bits=man))
    print(a - b)