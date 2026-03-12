# ========== 全局缓存 ==========
dp_cache = {}


# ========== 核心递归调度器 ==========
def dp(state, funcs):
    """通用的自顶向下记忆化搜索函数，funcs 包含 get_dependencies, transition, is_base"""
    # 1. 检查缓存
    if state in dp_cache:
        return dp_cache[state]

    # 2. 检查基础情况（如果提供了 is_base 函数）
    if 'is_base' in funcs:
        is_base_state, base_val = funcs['is_base'](state)
        if is_base_state:
            dp_cache[state] = base_val
            return base_val

    # 3. 获取依赖（必须提供）
    if 'get_dependencies' not in funcs:
        raise ValueError("funcs must contain 'get_dependencies'")
    deps = funcs['get_dependencies'](state)  # 返回字典 {标签: 子状态}

    # 4. 递归计算所有依赖
    dep_values = {}
    for key, dep_state in deps.items():
        dep_values[key] = dp(dep_state, funcs)

    # 5. 计算当前状态（必须提供）
    if 'transition' not in funcs:
        raise ValueError("funcs must contain 'transition'")
    result = funcs['transition'](state, dep_values)

    dp_cache[state] = result
    return result


# ========== 使用示例：斐波那契 ==========
fib_funcs = {
    'get_dependencies': lambda s: {'prev1': s - 1, 'prev2': s - 2},
    'transition': lambda s, deps: deps['prev1'] + deps['prev2'],
    'is_base': lambda s: (True, s) if s in (0, 1) else (False, None)
}


def fib(n):
    dp_cache.clear()  # 可选：清空缓存，避免多次调用相互干扰
    return dp(n, fib_funcs)


print(fib(10))  # 55

# ========== 使用示例：打家劫舍 ==========
# 假设房屋金额数组为全局变量 houses
houses = [2, 7, 9, 3, 1]


def rob_deps(state):
    # state 为房屋索引（0-based）
    return {'rob': state - 2, 'skip': state - 1}  # 注意依赖可能不存在，但 base_check 会处理


def rob_trans(state, deps):
    # deps 包含 'rob' 和 'skip' 的值（可能为 0 如果索引无效）
    rob_this = houses[state] + deps.get('rob', 0)  # 如果 'rob' 不存在则加 0
    skip_this = deps.get('skip', 0)
    return max(rob_this, skip_this)


def rob_base(state):
    if state < 0:
        return True, 0  # 超出范围的索引，收益为 0
    if state == 0:
        return True, houses[0]  # 只有一间房屋
    if state == 1:
        return True, max(houses[0], houses[1])  # 两间房屋
    return False, None


rob_funcs = {
    'get_dependencies': rob_deps,
    'transition': rob_trans,
    'is_base': rob_base
}


def rob(n):
    dp_cache.clear()
    return dp(n, rob_funcs)


print(rob(len(houses) - 1))  # 12
