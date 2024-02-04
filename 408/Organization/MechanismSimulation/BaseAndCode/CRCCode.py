crc32_poly = [32, 26, 23, 22, 16, 12, 11, 10, 8, 7, 5, 4, 2, 1, 0]
crc12_ploy = [12, 11, 3, 2, 1, 0]
crc4_poly = [4, 1, 0]


def poly_bin(crc_poly):
    length = crc_poly[0] + 1
    crc_poly_bin = [0] * length
    for i in range(0, len(crc_poly)):
        crc_poly_bin[length - crc_poly[i] - 1] = 1
    return crc_poly_bin


def crc_check(bin_list_src, crc_bin):
    bin_list = bin_list_src + ([0] * (len(crc_bin) - 1))
    slide_window = bin_list[0:len(crc_bin)]
    count = len(crc_bin)
    flag = True
    while count <= len(bin_list) and flag:
        if count == len(bin_list) and slide_window[0] == 0:
            break
        for i in range(0, len(slide_window)):
            slide_window[i] ^= crc_bin[i]
        if count == len(bin_list):
            flag = False
        while slide_window[0] == 0 and count < len(bin_list):
            slide_window.pop(0)
            slide_window.append(bin_list[count])
            count += 1
    return slide_window[1:], bin_list_src + slide_window[1:]


# crc_bin_poly = poly_bin([3, 2, 0])
check_code, full_bin = crc_check([1, 0, 1, 0, 1, 0, 1, 1], [1, 0, 0, 1, 1])
print('Done')
