from DPBottomUp import DPBottomUp
from GreedyProblem import GreedyProblem

act_list = [[0, 1], [0, 2], [1, 2], [2, 3], [2, 4]]
act_params = {"act_list": sorted(act_list, key=lambda x: (x[1], x[0]))}


# 1. 前驱候选（01贪心：只允许前面的状态）
def act_prev_candidates(params, state):
    _ = params
    return range(state)


# 2. 可行判断（活动不重叠）
def act_feasible(params, curr_state, prev_state):
    acts = params["act_list"]
    return acts[prev_state][1] <= acts[curr_state][0]


# 3. 贪心选择（选活动最多的）
def act_greedy_choice(depend_dp_dict, curr_state):
    _ = curr_state
    return max(depend_dp_dict, key=lambda s: len(depend_dp_dict[s]))


# 4. 最优子结构（拼接活动）
def act_optimal_substructure(prev_dp, curr_state, params):
    return prev_dp + [params["act_list"][curr_state]]


# 5. 初始状态（只选自己）
def act_initial_state(params, state):
    return [params["act_list"][state]]


# ==============================
# DP 底层逻辑（完全不变）
# ==============================
def act_base_check(state):
    return [act_params["act_list"][state]] if state == 0 else None


def act_walk_until(until):
    return list(range(until + 1))


def act_walk_step(state):
    return [state + 1]


# ==============================
# 测试运行
# ==============================
if __name__ == '__main__':
    # 1. 构造贪心问题（只传策略，不传数据）
    greedy = GreedyProblem(
        prev_candidates_generator=act_prev_candidates,
        feasible=act_feasible,
        greedy_choice=act_greedy_choice,
        optimal_substructure=act_optimal_substructure,
        initial_state=act_initial_state
    )

    # 2. 生成DP函数（params 只透传，不存储）
    depend = greedy.depend_func_factory(params=act_params)
    transit = greedy.transit_func_factory(params=act_params)

    # 3. 跑DP
    dp = DPBottomUp(
        transit_func=transit,
        depend_func=depend,
        walk_until=act_walk_until,
        walk_step=act_walk_step
    )
    dp.set_base_check(act_base_check)

    max_state = len(act_params["act_list"]) - 1
    dp.growth(until=max_state)

    best_result = None
    best_length = 0
    for state_ in range(max_state + 1):
        current_result = dp.query(state_)
        current_length = len(current_result)
        if current_length > best_length:
            best_length = current_length
            best_result = current_result

    print("最多活动数：", best_length)
    print("选中活动：", best_result)
