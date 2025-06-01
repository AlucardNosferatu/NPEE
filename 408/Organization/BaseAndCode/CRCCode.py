import random

crc32_poly = [32, 26, 23, 22, 16, 12, 11, 10, 8, 7, 5, 4, 2, 1, 0]
crc12_poly = [12, 11, 3, 2, 1, 0]
crc4_poly = [4, 1, 0]


def get_poly_bin(poly):
    length = poly[0] + 1
    poly_bin = [0] * length
    for i in range(0, len(poly)):
        poly_bin[length - poly[i] - 1] = 1
    return poly_bin


def get_crc(data_bin, poly_bin):
    bin_list = data_bin + ([0] * (len(poly_bin) - 1))
    slide_window = bin_list[0:len(poly_bin)]
    count = len(poly_bin)
    flag = True
    while count <= len(bin_list) and flag:
        if count == len(bin_list) and slide_window[0] == 0:
            break
        for i in range(0, len(slide_window)):
            slide_window[i] ^= poly_bin[i]
        if count == len(bin_list):
            flag = False
        while slide_window[0] == 0 and count < len(bin_list):
            slide_window.pop(0)
            slide_window.append(bin_list[count])
            count += 1
    return slide_window[1:], data_bin + slide_window[1:]


# crc_bin_poly = get_poly_bin(crc4_poly)
# check_code, full_bin = get_crc(data_bin=[1, 0, 1, 0, 1, 0, 1, 1], poly_bin=crc_bin_poly)
# print('Done')

def generate_polynomial_forms():
    # 生成5位二进制多项式（固定x⁴位为1）
    poly_bin = '1' + ''.join(random.choice('01') for _ in range(4))

    # 转换为自然形式（代数表达式）
    degree_map = {4: 'x⁴', 3: 'x³', 2: 'x²', 1: 'x', 0: '1'}
    natural_terms = []
    for i, bit in enumerate(poly_bin):
        if bit == '1':
            natural_terms.append(degree_map[4 - i])  # 最高位对应x⁴
    poly_natural = ' + '.join(natural_terms) if natural_terms else '0'

    # 转换为十六进制
    poly_hex = '0x' + format(int(poly_bin, 2), 'X')

    return {
        'binary': poly_bin,
        'natural': poly_natural,
        'hex': poly_hex
    }


def select_display_mode():
    modes = ['natural', 'binary', 'hex']
    weights = [0.7, 0.15, 0.15]  # 适当增加自然形式出现概率
    return random.choices(modes, weights=weights, k=1)[0]


def generate_question():
    # 生成随机数据（4-8位）
    data_bits = [random.choice([0, 1]) for _ in range(random.randint(4, 8))]

    # 获取多项式所有形式
    poly_forms = generate_polynomial_forms()
    poly_bin = [int(digit) for digit in list(poly_forms['binary'])]
    # 随机选择展示形式
    display_mode = select_display_mode()

    crc_result = get_crc(data_bits, poly_bin)

    mode_desc = {
        'natural': f"生成多项式{poly_forms['natural']}",
        'binary': f"二进制多项式{poly_forms['binary']}",
        'hex': f"十六进制多项式{poly_forms['hex']}"
    }
    question = f"数据{data_bits}使用多项式{mode_desc[display_mode]}进行CRC校验，计算得到的校验码是？"
    answer = f"校验码为：{crc_result[0]}，完整码字为：{crc_result[1]}"

    return question, answer


if __name__ == '__main__':
    # 示例输出
    q, a = generate_question()
    print("问题：", q)
    print("答案：", a)
