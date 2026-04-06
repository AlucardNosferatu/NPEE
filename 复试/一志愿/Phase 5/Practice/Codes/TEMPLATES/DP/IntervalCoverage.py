# IntervalCoverage_DPGreedy_Reconstructed.py

from DPGreedy import DPGreedy

test_cases = [
    ([0, 5], [[0, 3], [2, 5]], [[0, 3], [2, 5]]),
    ([0, 5], [[0, 3], [1, 4], [2, 5]], [[0, 3], [2, 5]]),
    ([0, 5], [[0, 2], [3, 5]], []),
    ([0, 5], [[0, 5], [1, 4]], [[0, 5]]),
    ([0, 9], [[1, 3], [2, 5], [0, 4], [3, 7], [5, 9], [6, 8]], [[0, 4], [3, 7], [5, 9]]),
]

cover_params = {
    "target": [],
    "intervals": [],
    "all_points": [],
    "point_to_idx": {},
}


def prev_candidates(params, state):
    _ = params
    # 返回所有更左的位置，防止环
    return list(range(state))


def feasible(params, curr_state, prev_state):
    # 松散检查：只要存在区间能从 prev_pos 到 curr_pos
    prev_pos = params["all_points"][prev_state]
    curr_pos = params["all_points"][curr_state]
    for s, e in params["intervals"]:
        if s <= prev_pos and e >= curr_pos:
            return True
    return False


def greedy_choice(depend_dp_dict, curr_state, params):
    _ = curr_state
    if not depend_dp_dict:
        return None
    # 选前驱位置中最远的（all_points 值最大）
    return max(depend_dp_dict.keys(), key=lambda idx: params["all_points"][idx])


def initial_state(params, state):
    """
    初始状态：从起点选能覆盖最远的区间，并跳步同步
    """
    dp = params['dp_injected']
    all_points = params["all_points"]
    intervals_sorted = params["intervals"]
    target_l = params["target"][0]
    curr_pos = all_points[state]

    best_end = target_l
    best_int = None
    for s_, e_ in intervals_sorted:
        if s_ <= target_l and e_ > best_end:
            best_end = e_
            best_int = [s_, e_]

    if best_int and best_end >= curr_pos:
        path = [best_int]
        # 跳步同步
        farthest_idx = next((i for i, p in enumerate(all_points) if p >= best_end), state)
        for sync in range(state, farthest_idx + 1):
            dp[sync] = path[:]
        return path
    return []


def optimal_substructure(prev_dp, curr_state, params):
    """
    从前驱路径终点出发，选最远区间推进，并跳步同步
    """
    dp = params['dp_injected']
    all_points = params["all_points"]
    intervals_sorted = params["intervals"]
    prev_path = prev_dp[:]

    prev_end = prev_path[-1][1] if prev_path else params["target"][0]
    # curr_pos = all_points[curr_state]

    best_interval = None
    farthest = prev_end
    for s_, e_ in intervals_sorted:
        if s_ <= prev_end and e_ > farthest:
            farthest = e_
            best_interval = [s_, e_]

    if best_interval and farthest > prev_end:
        new_path = prev_path + [best_interval]
        # 跳步同步
        farthest_idx = next((i for i, p in enumerate(all_points) if p >= farthest), curr_state)
        for sync in range(curr_state, farthest_idx + 1):
            dp[sync] = new_path[:]
        return new_path
    else:
        return prev_path


def walk_until(until):
    return list(range(until + 1))


def solve_interval_covering(target, intervals):
    target_l, target_r = target
    if target_l >= target_r:
        return []

    intervals_sorted = sorted(intervals, key=lambda x: x[0])
    points = {target_l, target_r}
    for s, e in intervals_sorted:
        points.add(s)
        points.add(e)
    all_points = sorted(points)
    point_to_idx = {p: i for i, p in enumerate(all_points)}
    target_idx = point_to_idx[target_r]

    cover_params["target"] = [target_l, target_r]
    cover_params["intervals"] = intervals_sorted
    cover_params["all_points"] = all_points
    cover_params["point_to_idx"] = point_to_idx

    dp = DPGreedy(
        prev_candidates_generator=prev_candidates,
        feasible=feasible,
        greedy_choice=greedy_choice,
        optimal_substructure=optimal_substructure,
        initial_state=initial_state,
        params=cover_params,
        walk_until=walk_until,
    )

    # 直接使用工厂生成的 transit_func
    dp.growth(target_idx)

    result = dp.query(target_idx)

    if not result or (result and result[-1][1] < target_r):
        for interval in intervals_sorted:
            s, e = interval
            if s <= target_l and e >= target_r:
                return [interval]
        return None

    return result


if __name__ == '__main__':
    for idx_, (target_, ints, expected) in enumerate(test_cases, 1):
        print(f"\n=== Test {idx_} ===")
        print(f"目标: {target_}")
        print(f"区间: {ints}")

        result_ = solve_interval_covering(target_, ints)

        print("得到:", result_)
        if result_ is None:
            print("状态: 无解")
        else:
            print(f"用了 {len(result_)} 个区间")

        pass_result = sorted(result_ or []) == sorted(expected)
        print("Pass:", pass_result)
