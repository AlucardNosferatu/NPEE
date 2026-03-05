from DP import DP

arr_ = []


def transit_func(depend_dp_dict, state):
    cms_im1 = depend_dp_dict['i-1'] + arr_[0][state]
    only_i = arr_[0][state]
    return max(cms_im1, only_i)


def depend_func(state):
    im1 = state - 1
    return {'i-1': im1}


if __name__ == '__main__':
    arr_.clear()
    arr_.append([1, 2])
    base_cases = {0: arr_[0][0]}
    K_CMS = DP(transit_func=transit_func, depend_func=depend_func, base_cases=base_cases)
    n = len(arr_[0])
    max_sub = 0
    for i in range(n):
        cur = K_CMS.query(i)
        if cur > max_sub:
            max_sub = cur

    print(max_sub)
