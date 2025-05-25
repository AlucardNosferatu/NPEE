import random


def generate_complement(bits=8):
    """生成指定位数的补码整数"""
    min_val = -2 ** (bits - 1)
    max_val = 2 ** (bits - 1) - 1
    return random.randint(min_val, max_val)


def to_bin_str(num, bits=8):
    """将补码整数转换为二进制字符串"""
    return bin(num & (2 ** bits - 1))[2:].zfill(bits)


def format_operand(num, bits, mode):
    """根据模式返回操作数描述"""
    if mode == 'bin':
        return f"的补码为{to_bin_str(num, bits)}"
    elif mode == 'dec':
        return f"为{num}（十进制）"
    return ""


def check_overflow(a, b, result, bits=8):
    """判断补码加减是否溢出（双符号位法）"""
    mask = (1 << (bits + 1)) - 1
    a_ext = a & mask
    b_ext = b & mask

    sum_ext = (a_ext + b_ext) & mask
    sign_bits = (sum_ext >> (bits - 1)) & 0b11

    return sign_bits in [0b01, 0b10]


def generate_question(bits=8):
    """生成一道题目和答案"""
    x = generate_complement(bits)
    y = generate_complement(bits)
    operator = random.choice(['+', '-'])

    # 随机选择每个操作数的显示模式
    x_mode = random.choice(['bin', 'dec'])
    y_mode = random.choice(['bin', 'dec'])

    # 生成题目描述
    x_desc = format_operand(x, bits, x_mode)
    y_desc = format_operand(y, bits, y_mode)
    question = f"已知X{x_desc}，Y{y_desc}，求[X{operator}Y]补，并判断是否溢出"

    # 计算结果
    if operator == '+':
        result = x + y
        overflow = check_overflow(x, y, result, bits)
    else:
        result = x - y
        overflow = check_overflow(x, -y, result, bits)

    return {
        "题目": question,
        "答案": {
            "运算结果补码": to_bin_str(result, bits),
            "溢出判断": "溢出" if overflow else "未溢出"
        }
    }


if __name__ == '__main__':
    question = generate_question()
    print(f"题目: {question['题目']}")
    print(f"答案: 结果补码={question['答案']['运算结果补码']}, {question['答案']['溢出判断']}\n")
