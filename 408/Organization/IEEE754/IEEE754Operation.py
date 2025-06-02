import random
import struct


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


def float_to_ieee(num):
    packed = struct.pack('>f', num)
    integer = struct.unpack('>I', packed)[0]
    sign = (integer >> 31) & 1
    exponent = (integer >> 23) & 0xFF
    mantissa = integer & 0x7FFFFF
    return sign, exponent, mantissa


def normalize(exponent, mantissa):
    if mantissa == 0:
        return exponent, mantissa
    while (mantissa & 0x800000) == 0:
        mantissa <<= 1
        exponent -= 1
    return exponent, mantissa


def generate_question():
    num1 = generate_float()
    num2 = generate_float()
    op = random.choice(['+', '-'])

    s1, e1, m1 = float_to_ieee(num1)
    s2, e2, m2 = float_to_ieee(num2)

    # 保留原始阶码用于显示
    original_e1 = e1
    original_e2 = e2

    # 对阶处理
    exp_diff = (e1 - 127) - (e2 - 127)
    if exp_diff > 0:
        m2 >>= exp_diff
        e2 = e1  # 小阶向大阶看齐
    elif exp_diff < 0:
        m1 >>= -exp_diff
        e1 = e2

    # 尾数运算（含隐藏位）
    if op == '+':
        res_mantissa = (0x800000 | m1) + (0x800000 | m2)
    else:
        res_mantissa = (0x800000 | m1) - (0x800000 | m2)

    # 规格化处理
    res_exp, res_mantissa = normalize(e1, res_mantissa)

    # 溢出判断
    overflow = (res_exp > 254) or (res_exp < 1)

    # 生成详细解答步骤
    steps = [
        f"题目：计算 {num1:.3f} {op} {num2:.3f}",
        "解题步骤：",
        "1. 原始IEEE754格式：",
        f"   {num1:.3f}: 符号位={s1}，阶码={original_e1 - 127}，尾数=1.{m1:023b}",
        f"   {num2:.3f}: 符号位={s2}，阶码={original_e2 - 127}，尾数=1.{m2:023b}",
        f"2. 对阶操作（阶差Δe={abs(exp_diff)}）：",
        f"   {'小阶' if exp_diff > 0 else '大阶'}数尾数右移{abs(exp_diff)}位",
        f"   对阶后公共阶码：{e1 - 127}",
        f"3. 尾数{op}运算：",
        f"   1.{m1:023b} {op} 1.{m2:023b} = 1.{res_mantissa:023b}",
        "4. 规格化处理：",
        f"   最终阶码={res_exp - 127}，规格化尾数=1.{res_mantissa:023b}",
        f"5. 溢出判断：{'发生上溢' if overflow else '未溢出'}"
    ]

    return '\n'.join(steps)


# 示例运行
print(generate_question())