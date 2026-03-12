from search import SearchEngine

# 假设你的 SearchEngine 类已经定义（这里省略，直接使用你的版本）

# 数据准备
arr = [1, 3, 5, 7, 9, 11, 13, 15]
target = 9  # 目标值，可修改

# 状态定义： (left, right, found, index)
# left, right: 当前搜索区间的左右边界（包含）
# found: 布尔值，表示是否已找到目标
# index: 当 found 为 True 时，记录目标索引
initial_state = (0, len(arr) - 1, False, -1)


def process_func(state, candidates):
    """根据当前区间，计算中间位置，比较后生成下一个区间（或找到状态）"""
    left, right, found, idx = state
    if found or left > right:
        # 已找到或区间无效，不再生成新状态
        return
    mid = (left + right) // 2
    if arr[mid] == target:
        # 找到目标，生成一个标记为 found 的状态
        new_state = (mid, mid, True, mid)
        candidates.append(new_state)
    elif arr[mid] < target:
        # 目标在右侧
        new_state = (mid + 1, right, False, -1)
        candidates.append(new_state)
    else:
        # 目标在左侧
        new_state = (left, mid - 1, False, -1)
        candidates.append(new_state)


def select_func(current_state, candidates):
    """从候选集中取出下一个状态（这里每次只有一个候选）"""
    _ = current_state
    if candidates:
        # 因为我们每次只生成一个候选，所以用 pop() 取出
        return candidates.pop()
    else:
        return None


def stop_cond_func(state):
    """终止条件：找到目标 或 区间无效"""
    left, right, found, idx = state
    return found or left > right


# 初始化引擎
initial_candidates = []  # 初始候选集为空
engine = SearchEngine(
    process_func=process_func,
    select_func=select_func,
    stop_cond_func=stop_cond_func,
    initial_state=initial_state,
    initial_candidates=initial_candidates
)

# 执行搜索
step = 0
while not engine.is_stopped():
    engine.step()
    print(f"Step {step}: {engine.current_state}")
    step += 1

# 输出结果
left_, right_, found_, idx_ = engine.current_state
if found_:
    print(f"找到目标 {target}，索引为 {idx_}")
else:
    print(f"未找到目标 {target}")
