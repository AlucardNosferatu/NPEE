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


def generate_question():
    # 生成随机数据（4-8位）
    data_bits = [random.choice([0, 1]) for _ in range(random.randint(4, 8))]

    # 随机选择多项式
    poly = random.choice([crc4_poly, crc12_poly])
    # poly = crc4_poly
    poly_bin = get_poly_bin(poly)

    # 生成完整CRC码（用于验证类问题）
    crc_result = get_crc(data_bits, poly_bin)

    question = f"数据{data_bits}使用多项式{poly}进行CRC校验，计算得到的校验码是？"
    answer = f"校验码为：{crc_result[0]}，完整码字为：{crc_result[1]}"

    return question, answer


if __name__ == '__main__':
    # 示例输出
    q, a = generate_question()
    print("问题：", q)
    print("答案：", a)
