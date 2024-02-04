def exponent_generate():
    pass


def exponent_code2number(exp_code):
    dec_exp = bin2number(exp_code)
    dec_exp -= 127
    return dec_exp


def mantissa_generate():
    pass


# sign,23,22,21,20...0
# sign,0,-1,-2,-3...-23
def mantissa_code2number(man_code):
    full_mc = [0, 1] + man_code
    assert len(full_mc) is 25
    # 23+2=25
    man_dec = bin2number(full_mc, shift=-23)
    return man_dec


# region basic_op
bin_flip = {0: 1, 1: 0}


# use reversed bin_code
# modified in situ
def bin_carry(bc_reversed, bit_index):
    if bc_reversed[bit_index] is 1 and bit_index + 1 < len(bc_reversed):
        bin_carry(bc_reversed, bit_index + 1)
    else:
        pass
    bc_reversed[bit_index] = bin_flip[bc_reversed[bit_index]]


def align_bits(bc_1, bc_2):
    size = max(len(bc_1), len(bc_2))
    while len(bc_1) < size:
        bc_1.insert(0, bc_1[0])
    while len(bc_2) < size:
        bc_2.insert(0, bc_2[0])
    return bc_1, bc_2


# bc_1=[0,1,1,0,0,0]
# bc_2=[1,1,1,1,0,1,0,0]
def bin_add(bin_code_1, bin_code_2):
    bc_1 = bin_code_1.copy()
    bc_2 = bin_code_2.copy()
    bc_1, bc_2 = align_bits(bc_1, bc_2)
    bc_1.reverse()
    bc_2.reverse()
    for i in range(0, len(bc_2)):
        if bc_2[i] is 1:
            bin_carry(bc_1, i)
    bc_1.reverse()
    return bc_1


# int_n=83
def number2bin(int_n):
    bin_list = []
    if int_n < 0:
        neg = True
    else:
        neg = False
    remain = abs(int_n)
    while remain is not 0:
        bin_list.append(remain % 2)
        remain /= 2
        remain = int(remain)
    bin_list.append(0)
    bin_list.reverse()
    if neg:
        for i in range(0, len(bin_list)):
            bin_list[i] = bin_flip[bin_list[i]]
        bin_list = bin_add(bin_list, [0, 1])
        bin_list[0] = 1
    return bin_list


# bin_code=[0,0,0,1,1,1,1,1]
def bin2number(bin_code, shift=0):
    bc_copy = bin_code.copy()
    sign = 1
    if bc_copy[0] is 1:
        for i in range(0, len(bc_copy)):
            bc_copy[i] = bin_flip[bc_copy[i]]
        bc_copy = bin_add(bc_copy, [0, 1])
        sign = -sign
    bc_copy.reverse()
    dec_val = 0
    for i in range(0, len(bc_copy) - 1):
        if bc_copy[i] is 1:
            dec_val += (2 ** (i + shift))
    dec_val *= sign
    return dec_val


# endregion

if __name__ is '__main__':
    # res = mantissa_code2number(
    #     [1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # )
    res = exponent_code2number([0, 1, 0, 0, 0, 0, 1, 0, 1])
    bin_list = number2bin(res)
    print(bin_list)
