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


def parse_ieee754(num):
    s, e, m = num
    sign = -1 if s == '1' else 1
    exponent = int(e, 2) - 127
    mantissa = 1.0 + int(m, 2) / (2 ** 23)
    return sign, exponent, mantissa


def align_exponents(E1, E2, M1, M2):
    if E1 > E2:
        delta_E = E1 - E2
        M2_aligned = M2 / (2 ** delta_E)
        return E1, M1, M2_aligned
    elif E2 > E1:
        delta_E = E2 - E1
        M1_aligned = M1 / (2 ** delta_E)
        return E2, M1_aligned, M2
    else:
        return E1, M1, M2


def compute_sign_and_magnitude(sign1, sign2, M1, M2, op):
    if op == '+':
        M_sum = sign1 * M1 + sign2 * M2
    elif op == '-':
        M_sum = sign1 * M1 - sign2 * M2
    else:
        raise ValueError("Unsupported operation")

    sign_result = 1 if M_sum >= 0 else -1
    M_sum_abs = abs(M_sum)
    return sign_result, M_sum_abs


def normalize_result(M_sum_abs, E_result):
    while M_sum_abs >= 2.0:
        M_sum_abs /= 2.0
        E_result += 1
    while M_sum_abs < 1.0 and M_sum_abs != 0:
        M_sum_abs *= 2.0
        E_result -= 1
    return M_sum_abs, E_result


def format_ieee754(sign_result, E_result, M_sum_abs):
    if M_sum_abs == 0:
        return '0', '00000000', '00000000000000000000000'

    fraction = M_sum_abs - 1.0
    mantissa = int(fraction * (2 ** 23))
    mantissa_bin = format(mantissa, '023b')

    exponent = E_result + 127
    exponent_bin = format(exponent, '08b')

    sign_bin = '1' if sign_result == -1 else '0'
    return sign_bin, exponent_bin, mantissa_bin


def ieee754_operation(op, num1, num2):
    # 解析IEEE754表示
    sign1, E1, M1 = parse_ieee754(num1)
    sign2, E2, M2 = parse_ieee754(num2)

    # 对阶
    E_aligned, M1_aligned, M2_aligned = align_exponents(E1, E2, M1, M2)

    # 尾数加减
    sign_result, M_sum_abs = compute_sign_and_magnitude(
        sign1, sign2, M1_aligned, M2_aligned, op
    )

    # 规格化处理
    M_normalized, E_normalized = normalize_result(M_sum_abs, E_aligned)

    # 格式化结果
    return format_ieee754(sign_result, E_normalized, M_normalized)



if __name__ == '__main__':
    a = generate_float()
    b = generate_float()
    print(a, b)
    a_ieee754 = float_to_ieee754(a)
    b_ieee754 = float_to_ieee754(b)
    print(a_ieee754)
    sign, exp, man = ieee754_operation('+', a_ieee754, b_ieee754)
    print(ieee754_to_float(sign_bit=sign, exponent_bits=exp, mantissa_bits=man))
    print(a + b)
    sign, exp, man = ieee754_operation('-', a_ieee754, b_ieee754)
    print(ieee754_to_float(sign_bit=sign, exponent_bits=exp, mantissa_bits=man))
    print(a - b)
