from DP import DP

# 用全局变量存放物品数据（也可放在闭包中）
weights = []
values = []


def depend_func(state):
    """给定状态 'i&c'，返回依赖的字典"""
    i, c = map(int, state.split('&'))
    deps = {'i-1&c': f"{i - 1}&{c}"}
    if c >= weights[i - 1]:
        deps['i-1&c-w'] = f"{i - 1}&{c - weights[i - 1]}"
    return deps


def transit_func(depend_dp_dict, state):
    """根据依赖的值计算当前状态"""
    # 从依赖字典中获取不选当前物品的值（一定存在）
    best = depend_dp_dict['i-1&c']
    # 如果存在选当前物品的依赖，则比较
    if 'i-1&c-w' in depend_dp_dict:
        candidate = depend_dp_dict['i-1&c-w'] + values[int(state.split('&')[0]) - 1]
        if candidate > best:
            best = candidate
    return best


def base_check(state):
    """基础情况：i==0 时价值为0"""
    i, _ = map(int, state.split('&'))
    if i == 0:
        return 0
    return None


if __name__ == '__main__':
    # 测试数据：4个物品，容量8
    weights = [2, 3, 4, 5]
    values = [3, 4, 5, 6]
    capacity = 8
    knap = DP(transit_func=transit_func, depend_func=depend_func)
    knap.set_base_check(base_check)
    result = knap.query(f"{len(weights)}&{capacity}")
    print("最大价值:", result)  # 应输出 10（选物品2和4，重量3+5=8，价值4+6=10）
