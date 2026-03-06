# ActivitySelection_DPGreedy.py

from DPGreedy import DPGreedy

act_params = {
    "act_list": [[0, 1], [0, 2], [1, 2], [2, 3], [2, 4]],
}

act_params["act_list"] = sorted(act_params["act_list"], key=lambda x: (x[1], x[0]))


def prev_candidates(params, state):
    _ = params
    # 前驱是所有比当前 state 小的活动
    return list(range(state))


def feasible(params, curr_state, prev_state):
    acts = params["act_list"]
    return acts[prev_state][1] <= acts[curr_state][0]


def greedy_choice(depend_dp_dict, curr_state):
    _ = curr_state
    # 选择能带来最多活动的路径
    return max(depend_dp_dict, key=lambda k: len(depend_dp_dict[k]))


def optimal_substructure(prev_dp, curr_state, params):
    return prev_dp + [params["act_list"][curr_state]]


def initial_state(params, state):
    return [params["act_list"][state]]


def walk_until(until):
    return list(range(until + 1))


def base_check(state):
    if state == 0:
        return [act_params["act_list"][0]]
    return None


if __name__ == '__main__':
    n = len(act_params["act_list"])

    dp = DPGreedy(
        prev_candidates_generator=prev_candidates,
        feasible=feasible,
        greedy_choice=greedy_choice,
        optimal_substructure=optimal_substructure,
        initial_state=initial_state,
        params=act_params,
        walk_until=walk_until,
    )
    dp.set_base_check(base_check)

    dp.growth(until=n - 1)

    # 找最优解（活动选择找最大数量）
    best_path = None
    best_len = 0
    for i in range(n):
        path = dp.query(i)
        if path and len(path) > best_len:
            best_len = len(path)
            best_path = path

    print("最多活动数:", best_len)
    print("选中活动:", best_path)
