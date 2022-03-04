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


def test():
    dec = random.randint(0, 65535)
    w = dec2bin_weights(dec)
    d = weight2digit(w)
    b = digit2bin(d)
    h = bin2hex(b)
    print(h)
