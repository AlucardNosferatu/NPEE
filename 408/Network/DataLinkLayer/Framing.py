dict_bl = {'01000111': 'A', '11100011': 'B', '11100000': 'ESC', '01111110': 'FLAG'}


def char_count(bytes_list):
    bl_new = bytes_list.copy()
    length = len(bl_new)
    length += 1
    length = bin(length).split('b')[1]
    while len(length) < 8:
        length = '0' + length
    bl_new.insert(0, length)
    return bl_new


def soh_and_eot(bytes_list):
    bl_new = bytes_list.copy()
    i = 0
    while i < len(bl_new):
        if bl_new[i] in ['11100000', '01111110']:
            bl_new.insert(i, '11100000')
            i += 1
        i += 1
    bl_new = ['01111110'] + bl_new + ['01111110']
    return bl_new


def bit_filling(bytes_list):
    bl_new = bytes_list.copy()
    bin_list = []
    for i in bl_new:
        for j in i:
            bin_list.append(int(j))
    bit_1_count = 0
    i = 0
    while i < len(bin_list):
        if bin_list[i] == 1:
            bit_1_count += 1
            if bit_1_count == 5:
                bin_list.insert(i + 1, 0)
                bit_1_count = 0
                i += 1
        else:
            bit_1_count = 0
        i += 1
    bin_list = [0, 1, 1, 1, 1, 1, 1, 0] + bin_list + [0, 1, 1, 1, 1, 1, 1, 0]
    return bin_list


def check_dict(bytes_list):
    for i in bytes_list:
        if i in dict_bl:
            print(dict_bl[i])
        else:
            print(i)


bl = ['01000111', '11100011', '11100000', '01111110']
cc = char_count(bl)
sae = soh_and_eot(bl)
bf = bit_filling(bl)

print('Done')
