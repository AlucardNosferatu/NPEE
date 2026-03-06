# IntervalCoverage_DPGreedy_Final.py

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
    # 為了讓 Kahn 排序正常，返回所有更左的位置（簡單實現）
    return list(range(state))


def feasible(params, curr_state, prev_state):
    # 只要存在區間能從 prev 到 curr 即可（鬆散，靠 transit 篩選）
    prev_pos = params["all_points"][prev_state]
    curr_pos = params["all_points"][curr_state]
    for s, e in params["intervals"]:
        if s <= prev_pos and e >= curr_pos:
            return True
    return False


def greedy_choice(depend_dp_dict, curr_state, params):
    _, _ = curr_state, params
    # 選最遠的前位置
    if not depend_dp_dict:
        return None
    return max(depend_dp_dict.keys(), key=lambda idx: cover_params["all_points"][idx])


def optimal_substructure(prev_dp, curr_state, params):
    _, _ = curr_state, params
    # 占位，返回 prev_dp（追加在 transit_func 裡完成）
    return prev_dp


def initial_state(params, state):
    _, _ = params, state
    return []


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

    # 核心：自定義 transit_func，支持跳步同步
    def custom_transit(depend_dp_dict, state):
        curr_pos = all_points[state]

        if not depend_dp_dict:
            # 初始：選起點能覆蓋的最遠區間
            best_end = target_l
            best_int = None
            for interval_ in intervals_sorted:
                s_, e_ = interval_
                if s_ <= target_l and e_ > best_end:
                    best_end = e_
                    best_int = [s_, e_]
            if best_int and best_end >= curr_pos:
                path = [best_int]
                # 跳步同步
                farthest_idx = next((i for i, p in enumerate(all_points) if p >= best_end), state)
                for sync in range(state, farthest_idx + 1):
                    dp.dp[sync] = path[:]
                return path
            return []

        # 正常流程
        best_prev = greedy_choice(depend_dp_dict, state, cover_params)
        if best_prev is None:
            return []

        prev_path = depend_dp_dict[best_prev]
        prev_end = prev_path[-1][1] if prev_path else target_l

        # 貪心選最遠區間
        best_interval = None
        farthest = prev_end
        for interval_ in intervals_sorted:
            s_, e_ = interval_
            if s_ <= prev_end and e_ > farthest:
                farthest = e_
                best_interval = [s_, e_]

        if best_interval and farthest > prev_end:
            new_path = prev_path + [best_interval]
            # 跳步同步
            farthest_idx = next((i for i, p in enumerate(all_points) if p >= farthest), state)
            for sync in range(state, farthest_idx + 1):
                dp.dp[sync] = new_path[:]
            return new_path
        else:
            return prev_path

    dp.transit_func = custom_transit

    dp.growth(target_idx)

    result = dp.dp.get(target_idx, None)
    if result is None:
        result = dp.query(target_idx)  # 兜底

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
        print(f"目標: {target_}")
        print(f"区间: {ints}")

        result_ = solve_interval_covering(target_, ints)

        print("得到:", result_)
        if result_ is None:
            print("状态: 无解")
        else:
            print(f"用了 {len(result_)} 个区间")

        pass_result = sorted(result_ or []) == sorted(expected)
        print("Pass:", pass_result)
