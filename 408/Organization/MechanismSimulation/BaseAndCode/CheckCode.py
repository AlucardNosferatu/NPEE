import random

# 0 for even
# 1 for odd
from BaseAndCode.BaseConv import dec2bin_weights, weight2digit, digit2bin


def parity(bin_list):
    result = bin_list[0]
    for i in range(1, len(bin_list)):
        result ^= bin_list[i]
    return result


def hamming_code_check_digits(bin_list):
    n = len(bin_list)
    k = 0
    while 2 ** k < n + k + 1:
        k += 1
    check_digits_pos = []
    for i in range(0, k):
        check_digits_pos.append(2 ** i)
    length = n + k
    return check_digits_pos, length


def hamming_code_group(bin_list, check_digits_pos):
    groups_list = {}
    bl_len = len(bin_list) + len(check_digits_pos)
    for pos in check_digits_pos:
        w = dec2bin_weights(pos)
        d = weight2digit(w)
        b = digit2bin(d)
        check_bit_pos = b.index(1)
        group_list = []
        for i in range(1, bl_len + 1):
            wi = dec2bin_weights(i)
            di = weight2digit(wi)
            bi = digit2bin(di)
            if bi[check_bit_pos] == 1:
                group_list.append(i)
        groups_list[pos] = group_list
    return groups_list


def hamming_code_check(bin_list, check_digits_pos, groups_list):
    length = len(bin_list) + len(check_digits_pos)
    ham_template = [0] * length
    j = 0
    for i in range(0, len(ham_template)):
        if (length - i) not in check_digits_pos:
            ham_template[i] = bin_list[j]
            j += 1
    p_bits = []
    for i in range(0, len(ham_template)):
        if (length - i) in check_digits_pos:
            xor_res = 0
            for info_bit in groups_list[length - i]:
                if info_bit != length - i:
                    xor_res ^= ham_template[length - info_bit]
            ham_template[i] = xor_res
            p_bits.append(xor_res)
    return ham_template, p_bits


bl = [1, 0, 1, 0, 1, 0]
cdp, le = hamming_code_check_digits(bl)
gl = hamming_code_group(bl, cdp)
hc, pb = hamming_code_check(bl, cdp, gl)
print('Done')
