import random


def int_to_bin(n, bits=8):
    """整数转二进制字符串（含符号位）"""
    if n >= 0:
        return '0' + bin(n)[2:].zfill(bits - 1)
    else:
        return '1' + bin(n & ((1 << (bits - 1)) - 1))[2:].zfill(bits - 1)


def complement(code):
    """补码转换（输入为二进制字符串）"""
    if code[0] == '0':
        return code  # 正数补码不变
    # 负数补码转原码：取反加1
    inverted = ''.join('1' if c == '0' else '0' for c in code[1:])
    return '1' + bin(int(inverted, 2) + 1)[2:].zfill(len(code) - 1)


def inverse(code):
    """反码转换（输入为二进制字符串）"""
    if code[0] == '0':
        return code  # 正数反码不变
    return '1' + ''.join('1' if c == '0' else '0' for c in code[1:])


def shift_code(code):
    """移码转换（输入为补码）"""
    sign_bit = '1' if code[0] == '0' else '0'  # 符号位取反
    return sign_bit + code[1:]


def generate_question():
    # 随机生成数值和转换类型
    number = random.randint(-255, 127)
    if number < -127:
        number = round(number / 2)
    conversions = [
        ('原码转补码', '补码'),
        ('补码转原码', '原码'),
        ('原码转反码', '反码'),
        ('反码转原码', '原码'),
        ('补码转移码', '移码')
    ]
    conv_type, target = random.choice(conversions)

    # 生成原码/补码作为题目基础
    original_code = int_to_bin(number, 8)
    if conv_type.startswith('补码'):
        base_code = int_to_bin(number, 8) if number >= 0 else int_to_bin(number + (1 << 7), 8)
    else:
        base_code = original_code

    # 生成题目和答案
    question = f"将二进制{base_code}的{conv_type.split('转')[0]}转换为{target}："

    if conv_type == '原码转补码':
        answer = int_to_bin(number, 8) if number >= 0 else int_to_bin(number + (1 << 7), 8)
    elif conv_type == '补码转原码':
        answer = complement(base_code)
    elif conv_type == '原码转反码':
        answer = inverse(base_code)
    elif conv_type == '反码转原码':
        answer = inverse(base_code)  # 反码与原码转换对称
    elif conv_type == '补码转移码':
        answer = shift_code(base_code)
    else:
        raise ValueError('题型错误！')

    return question, answer


if __name__ == '__main__':
    # 示例运行
    q, a = generate_question()
    print("题目：", q)
    print("答案：", a)
    print("---")
