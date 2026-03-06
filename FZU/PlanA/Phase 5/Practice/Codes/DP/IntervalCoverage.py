from DPBottomUp import DPBottomUp
from Greedy import GreedyFactory

# ──────────────────────────────────────────────
# 测试数据（可自行补全所有用例）
# ──────────────────────────────────────────────

test_cases = [
    # 1. 简单两个区间
    ([0, 5], [[0, 3], [2, 5]], [[0, 3], [2, 5]]),
    # 3. 应该选 [0,3] + [2,5]
    ([0, 5], [[0, 3], [1, 4], [2, 5]], [[0, 3], [2, 5]]),
    # 5. 有缺口 → 无解
    ([0, 5], [[0, 2], [3, 5]], []),
    # 6. 单个区间直接覆盖
    ([0, 5], [[0, 5], [1, 4]], [[0, 5]]),
    # 7. 经典例子
    ([0, 9], [[1, 3], [2, 5], [0, 4], [3, 7], [5, 9], [6, 8]], [[0, 4], [3, 7], [5, 9]]),
]

# ──────────────────────────────────────────────
# 全局透传参数
# ──────────────────────────────────────────────

cover_params = {
    "target_L": 0,
    "target_R": 0,
    "intervals": [],
    "all_points": [],
    "point_to_idx": {},
    "__current_cover_pos__": 0,
}


# 1. 前驱候选
def cover_prev_candidates(params, state):
    _ = params
    return list(range(state))


# 2. 可行判断
def cover_feasible(params, curr_state, prev_state):
    prev_pos = params["all_points"][prev_state]
    curr_pos = params["all_points"][curr_state]
    for s, e in params["intervals"]:
        if s <= prev_pos and e >= curr_pos:
            return True
    return False


# 3. 贪心选择（仅用于选一条前驱路径，这里选最短路径）
def cover_greedy_choice(depend_dp_dict, curr_state):
    _ = curr_state
    if not depend_dp_dict:
        return None
    return min(depend_dp_dict.keys(), key=lambda k: len(depend_dp_dict[k]))


# 4. 转移函数（核心修正版）
def cover_transit(params):
    intervals = params["intervals"]
    all_points = params["all_points"]
    target_l = params["target_l"]

    def transit_func(depend_dp_dict, state):
        curr_pos = all_points[state]
        params["__current_cover_pos__"] = curr_pos

        # ──────────────── 情况1：起点（无前驱）
        if not depend_dp_dict:
            best_interval = None
            max_reach = target_l
            for interval in intervals:
                s, e = interval
                if s <= target_l and e > max_reach:
                    max_reach = e
                    best_interval = interval
            if best_interval and max_reach >= curr_pos:
                return [best_interval[:]]  # 复制列表
            return []

        # ──────────────── 情况2：有前驱
        # 选一条前驱路径（最短的）
        best_prev_path = []
        prev_end = target_l
        if depend_dp_dict:
            best_prev_key = cover_greedy_choice(depend_dp_dict, state)
            if best_prev_key is not None:
                best_prev_path = depend_dp_dict[best_prev_key]
                if best_prev_path:
                    prev_end = best_prev_path[-1][1]

        # 从 prev_end 开始贪心选最远区间
        best_interval = None
        farthest = prev_end
        for interval in intervals:
            s, e = interval
            if s <= prev_end and e > farthest:
                farthest = e
                best_interval = interval

        # 只有真正推进了且能覆盖到 curr_pos 才追加
        if farthest > prev_end and farthest >= curr_pos and best_interval is not None:
            return best_prev_path + [best_interval[:]]  # 复制

        # 否则返回当前路径（不加任何东西，更不会加 None）
        return best_prev_path[:] if best_prev_path else []

    return transit_func


# 5. 初始状态（备用，几乎不用）
def cover_initial_state(params, state):
    _, _ = params, state
    return []


# 6. 走访
def cover_walk_until(until):
    return list(range(until + 1))


# ──────────────────────────────────────────────
# 主求解函数
# ──────────────────────────────────────────────

def solve_interval_covering(target, intervals):
    l_bound, r_bound = target
    if l_bound >= r_bound:
        return []

    # 离散点
    points = {l_bound, r_bound}
    for s, e in intervals:
        points.add(s)
        points.add(e)
    all_points = sorted(points)
    point_to_idx = {p: i for i, p in enumerate(all_points)}

    # 更新 params
    cover_params["target_L"] = l_bound
    cover_params["target_R"] = r_bound
    cover_params["intervals"] = sorted(intervals, key=lambda x: x[0])
    cover_params["all_points"] = all_points
    cover_params["point_to_idx"] = point_to_idx

    # 构造 GreedyProblem
    greedy = GreedyFactory(
        prev_candidates_generator=cover_prev_candidates,
        feasible=cover_feasible,
        greedy_choice=cover_greedy_choice,
        optimal_substructure=lambda prev, curr, p: prev,  # 合并已移到 transit_func
        initial_state=cover_initial_state
    )

    depend = greedy.depend_func_factory(params=cover_params)
    transit = cover_transit(cover_params)

    dp = DPBottomUp(
        transit_func=transit,
        depend_func=depend,
        walk_until=cover_walk_until,
    )

    target_idx = point_to_idx[r_bound]

    # 计算
    dp.growth(until=target_idx)

    result = dp.query(target_idx)

    # 最终检查
    if result is None or not result:
        # 检查是否有单区间直接覆盖
        for interval in cover_params["intervals"]:
            s, e = interval
            if s <= l_bound and e >= r_bound:
                return [interval[:]]
        return None

    # 检查是否覆盖到终点
    if result and result[-1][1] >= r_bound:
        return result
    else:
        return None


if __name__ == '__main__':
    for idx, (target_, intervals_, expected) in enumerate(test_cases, 1):
        print(f"\n测试用例 {idx}")
        print("目标:", target_)
        print("区间:", intervals_)

        ans = solve_interval_covering(target_, intervals_)

        print("得到:", ans)
        if ans is None:
            print("状态: 无解")
        else:
            print(f"用了 {len(ans)} 个区间")

        # 判断
        if ans is None:
            print("预期无解 →", expected == [])
        else:
            # 忽略顺序比较
            print("结果是否匹配预期（忽略顺序）:", sorted(ans or []) == sorted(expected))
