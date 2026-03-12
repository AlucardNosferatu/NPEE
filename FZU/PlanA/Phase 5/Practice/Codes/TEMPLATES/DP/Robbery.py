from DP import DP

nums_ = []


def transit_func(depend_dp_dict, state):
    rob = depend_dp_dict['i+2'] + nums_[0][state]
    skip = depend_dp_dict['i+1']
    return max(rob, skip)


def depend_func(state):
    ip1 = state + 1
    ip2 = state + 2
    return {
        'i+1': ip1,
        'i+2': ip2
    }


def base_check(state):
    if state >= len(nums_[0]):
        return 0
    else:
        return None


if __name__ == '__main__':
    nums_.clear()
    nums_.append([2, 7, 9, 3, 1])
    Robbery = DP(transit_func=transit_func, depend_func=depend_func)
    Robbery.set_base_check(base_check=base_check)
    res = Robbery.query(0)
    print(res)
