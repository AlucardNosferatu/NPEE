def dec2bcd_digits(dec):
    r = 0
    while 10 ** r < dec:
        r += 1
    r = r - 1
    dec_d = []
    for i in range(0, r + 1):
        dec_d.append(int(dec / (10 ** (r - i))))
        dec %= (10 ** (r - i))
    return dec_d


def dec2bcd_d2b(dec_d):
    bin_4d_list = []
    bin_4d_map = [
        [0, 0, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 0, 1, 1],
        [0, 1, 0, 0],
        [0, 1, 0, 1],
        [0, 1, 1, 0],
        [0, 1, 1, 1],
        [1, 0, 0, 0],
        [1, 0, 0, 1],
        [1, 0, 1, 0],
        [1, 0, 1, 1],
        [1, 1, 0, 0],
        [1, 1, 0, 1],
        [1, 1, 1, 0],
        [1, 1, 1, 1]
    ]
    for dec in dec_d:
        bin_4d_list += bin_4d_map[dec]
    return bin_4d_list


dec_digits = dec2bcd_digits(3456)
bin_list = dec2bcd_d2b(dec_digits)
print('Done')
