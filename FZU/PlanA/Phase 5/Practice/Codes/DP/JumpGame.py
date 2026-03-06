# JumpGameII_DPGreedy.py
# 给定一个非负整数数组 nums，你从数组的第一个位置开始。
# 数组中的每个元素代表你在该位置可以跳跃的最大距离。
# 你的目标是用最少的跳跃次数到达数组的最后一个位置。
# 示例：
# nums = [2,3,1,1,4] → 2（0 → 1 → 4）
from DPGreedy import DPGreedy

test_cases = [
    ([2, 3, 1, 1, 4], 2),
    ([2, 3, 0, 1, 4], 2),
    ([1, 1, 1, 1], 3),
    ([0], 0),
    ([1, 2], 1),
]

jump_params = {
    "nums": [],
    "n": 0,
}


def prev_candidates(params, state):
    # state = 当前位置索引
    # 前驱是所有能跳到 state 的前位置
    candidates = []
    for prev in range(state):
        if prev + params["nums"][prev] >= state:
            candidates.append(prev)
    return candidates


def feasible(params, curr_state, prev_state):
    # prev_state 是否能跳到 curr_state
    return prev_state + params["nums"][prev_state] >= curr_state


def greedy_choice(depend_dp_dict, curr_state):
    # 选跳跃次數最少的前驱（最优子问题）
    if not depend_dp_dict:
        return None
    return min(depend_dp_dict, key=lambda k: depend_dp_dict[k])


def optimal_substructure(prev_dp, curr_state, params):
    # prev_dp 是跳跃次数
    return prev_dp + 1


def initial_state(params, state):
    if state == 0:
        return 0
    return float('inf')  # 无法到达


def walk_until(until):
    return list(range(until + 1))


def solve_jump_game(nums):
    n = len(nums)
    if n <= 1:
        return 0

    jump_params["nums"] = nums
    jump_params["n"] = n

    dp = DPGreedy(
        prev_candidates_generator=prev_candidates,
        feasible=feasible,
        greedy_choice=greedy_choice,
        optimal_substructure=optimal_substructure,
        initial_state=initial_state,
        params=jump_params,
        walk_until=walk_until,
    )

    dp.growth(until=n - 1)

    result = dp.query(n - 1)

    return result if result != float('inf') else -1  # -1 表示无法到达


if __name__ == '__main__':
    for idx, (nums, expected) in enumerate(test_cases, 1):
        print(f"\n=== Test {idx} ===")
        print(f"nums: {nums}")
        result = solve_jump_game(nums)
        print("最少跳跃次数:", result)
        print("Pass:", result == expected)
