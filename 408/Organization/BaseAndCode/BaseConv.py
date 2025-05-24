import random

bin2hex_4bin = [
    [
        [
            ['0', '1'],
            ['2', '3']
        ],
        [
            ['4', '5'],
            ['6', '7']
        ]
    ],
    [
        [
            ['8', '9'],
            ['A', 'B']
        ],
        [
            ['C', 'D'],
            ['E', 'F']
        ]
    ]
]


def binary_gen(n=8):
    b_code = [0] * n
    bit1_count = random.randint(1, len(b_code))
    for i in range(0, bit1_count):
        bit1_pos = random.randint(0, len(b_code) - 1)
        b_code[bit1_pos] = 1
    return b_code


def bin2hex_align(bin_list):
    suffix_length = 4 - (len(bin_list) % 4)
    for i in range(0, suffix_length):
        bin_list.insert(0, 0)
    return bin_list


def bin2hex(bin_list):
    hex_list = []
    for i in range(0, len(bin_list), 4):
        temp_list = bin_list[i:i + 4]
        hex_list.append(
            bin2hex_4bin[temp_list[0]][temp_list[1]][temp_list[2]][temp_list[3]]
        )
    return hex_list


def dec2bin_weights(dec_int):
    weights = []
    while True:
        weight = 0
        while 2 ** weight <= dec_int:
            weight += 1
        if weight > 0:
            dec_int -= (2 ** (weight - 1))
            weights.append(weight - 1)
        else:
            break
    return weights


def weight2digit(weights):
    return [item + 1 for item in weights]


def digit2bin(digits):
    length_time = 0
    while 4 * length_time < digits[0]:
        length_time += 1
    bin_template = [0] * (length_time * 4)
    for i in range(0, len(digits)):
        bin_template[4 * length_time - digits[i]] = 1
    return bin_template


def func_test():
    dec = random.randint(0, 65535)
    w = dec2bin_weights(dec)
    d = weight2digit(w)
    b = digit2bin(d)
    h = bin2hex(b)
    print(h)


def generate_conversion_qa():
    # 生成随机十进制数（范围可调）
    dec_num = random.randint(1, 65535)

    # 转换流程
    weights = dec2bin_weights(dec_num)  # [[4]]
    digits = weight2digit(weights)  # [[4]]
    bin_list = digit2bin(digits)  # [[4]]
    hex_result = ''.join(bin2hex(bin_list))  # [[4]]

    # 构造二进制字符串（处理前导零）
    bin_str = ''.join(map(str, bin_list)).lstrip('0') or '0'

    # 生成格式化输出
    question = f"将十进制数 {dec_num} 转换为二进制和十六进制表示"
    answer = f"二进制：{bin_str}\n十六进制：0x{hex_result.upper()}"

    return question, answer


if __name__ == '__main__':
    # 示例使用
    q, a = generate_conversion_qa()
    print("问题：", q)
    print("答案：", a)
