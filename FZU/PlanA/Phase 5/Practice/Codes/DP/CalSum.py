from DP import DP

nums_ = []
target_ = []


def transit_func(depend_dp_dict, state):
    _ = state
    add = depend_dp_dict['i+1&j+ni']
    sub = depend_dp_dict['i+1&j-ni']
    return add + sub


def depend_func(state):
    n = state.split('&')
    i = int(n[0])
    j = int(n[1])
    ip1 = i + 1
    ni = nums_[0][i]
    j_p_ni = j + ni
    j_m_ni = j - ni
    return {
        'i+1&j+ni': str(ip1) + '&' + str(j_p_ni),
        'i+1&j-ni': str(ip1) + '&' + str(j_m_ni)
    }


def base_check(state):
    state = state.split('&')
    i = int(state[0])
    j = int(state[1])
    if i == len(nums_[0]):
        if j == target_[0]:
            return 1
        else:
            return 0
    else:
        return None


if __name__ == '__main__':
    nums_.clear()
    target_.clear()
    nums_.append([1, 1, 1, 1, 1])
    target_.append(3)
    CalSum = DP(transit_func=transit_func, depend_func=depend_func)
    CalSum.set_base_check(base_check=base_check)
    res = CalSum.query('0&0')
    print(res)
