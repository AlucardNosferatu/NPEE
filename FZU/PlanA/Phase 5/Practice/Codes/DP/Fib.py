from DPBottomUp import DPBottomUp


def fib_depend_func(state):
    return {'n-1': state - 1, 'n-2': state - 2}


def fib_transit_func(depend_dp_dict, state):
    _ = state
    nm1 = depend_dp_dict['n-1']
    nm2 = depend_dp_dict['n-2']
    return nm1 + nm2


def fib_walk_until(until):
    return list(range(until + 1))


def fib_walk_step(state):
    return [state + 1, state + 2]


fib_base_cases = {0: 0, 1: 1}
stairs_base_cases = {0: 0, 1: 1, 2: 2}

if __name__ == '__main__':
    # Fib = DP(transit_func=fib_transit_func, depend_func=fib_depend_func, base_cases=stairs_base_cases)
    Fib = DPBottomUp(
        transit_func=fib_transit_func, depend_func=fib_depend_func, base_cases=fib_base_cases,
        # walk_until=fib_walk_until,
        walk_until=None,
        walk_step=fib_walk_step
    )
    # for i in range(0, 20):
    #     res = Fib.query(i)
    #     print(res)
    Fib.growth(until=20)
