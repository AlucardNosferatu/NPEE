def cmm(input_list: list):
    input_list_ = input_list.copy()
    input_list_.reverse()
    output_list = []
    max_pos = None
    max_neg = None
    min_pos = None
    min_neg = None
    for val in input_list_:
        if max_pos is None or max_pos <= 0 or val > max_pos > 0:
            max_pos = val
        if max_neg is None or max_neg > 0 or 0 >= val > max_neg:
            max_neg = val
        if min_pos is None or min_pos < 0 or min_pos > val >= 0:
            min_pos = val
        if min_neg is None or min_neg >= 0 or 0 > min_neg > val:
            min_neg = val
        if val >= 0:
            res1 = val * max_pos
            res2 = val * max_neg
            if res1 > res2:
                res = res1
            else:
                res = res2
        else:
            res1 = val * min_neg
            res2 = val * min_pos
            if res1 > res2:
                res = res1
            else:
                res = res2
        output_list.append(res)
    output_list.reverse()
    return output_list


if __name__ == '__main__':
    i_list = [0, -5, 0, 6, -2]
    o_list = cmm(input_list=i_list)
    print(o_list)
