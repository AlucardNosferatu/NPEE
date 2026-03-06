# ShortestPathDAG_DPGreedy.py
from DPGreedy import DPGreedy


def solve_shortest_path_dag(graph, source):
    """
    使用 DPGreedy 求解 DAG 上的单源最短路径。
    graph : 邻接表，格式 {u: [(v, weight), ...]}，保证为 DAG。
    source: 源点。
    返回 (dist_dict, prev_dict)
    """
    nodes = list(graph.keys())
    # 为简化，假设节点编号连续且可作为状态
    dijkstra_params = {
        'graph': graph,
        'source': source,
        'prev': {},  # 前驱表（用于重建路径）
        'pq': [],  # 占位优先队列（DAG 中不需要）
        '_best_prev': {}  # 内部暂存每个状态的最佳前驱
    }

    # ---------- 工厂函数 ----------
    def prev_candidates(params, state):
        _, _ = params, state
        """返回所有可能的候选前驱（后续由 feasible 过滤）"""
        return nodes

    def feasible(params, curr_state, prev_state):
        """检查 prev_state 是否有边指向 curr_state"""
        for v, _ in params['graph'].get(prev_state, []):
            if v == curr_state:
                return True
        return False

    def greedy_choice(depend_dp_dict, curr_state, params):
        """
        从所有可行前驱中选择使「前驱距离 + 边权」最小的前驱。
        将选中的前驱存入 params['_best_prev'] 供 optimal_substructure 使用。
        """
        best_prev = None
        best_total = float('inf')
        for prev_state, prev_dist in depend_dp_dict.items():
            # 找到从 prev 到 curr 的最小边权（可能有平行边）
            min_weight = float('inf')
            for v, w in params['graph'].get(prev_state, []):
                if v == curr_state and w < min_weight:
                    min_weight = w
            if min_weight == float('inf'):
                continue
            cand = prev_dist + min_weight
            if cand < best_total:
                best_total = cand
                best_prev = prev_state
        params['_best_prev'][curr_state] = best_prev
        return best_prev

    def optimal_substructure(prev_dp, curr_state, params):
        """
        根据最佳前驱的距离和边权计算当前状态的距离，
        同时记录前驱用于路径重建。
        """
        best_prev = params['_best_prev'].get(curr_state)
        if best_prev is None:
            return float('inf')
        # 获取对应的边权
        weight = None
        for v, w in params['graph'].get(best_prev, []):
            if v == curr_state:
                weight = w
                break
        if weight is None:
            return float('inf')
        curr_dp = prev_dp + weight
        # 记录前驱
        params['prev'][curr_state] = best_prev
        return curr_dp

    def initial_state(params, state):
        _, _ = params, state
        """没有前驱时返回无穷大（不可达）"""
        return float('inf')

    def walk_until(until):
        """返回所有节点（假设节点编号从 0 到 until）"""
        return list(range(until + 1))

    # ---------- 构造 DPGreedy 实例 ----------
    dp_solver = DPGreedy(
        prev_candidates_generator=prev_candidates,
        feasible=feasible,
        greedy_choice=greedy_choice,
        optimal_substructure=optimal_substructure,
        initial_state=initial_state,
        params=dijkstra_params,
        base_cases={source: 0},  # 源点作为 base case
        walk_until=walk_until
    )

    # 执行计算
    max_node = max(nodes)
    dp_solver.growth(until=max_node)

    # 收集结果
    dist = {node_: dp_solver.query(node_) for node_ in nodes}
    return dist, dijkstra_params['prev']


# ========== 测试 ==========
if __name__ == '__main__':
    # 定义一个有向无环图
    graph_ = {
        0: [(1, 4), (2, 1)],
        1: [(3, 1)],
        2: [(1, 2), (3, 5)],
        3: []
    }
    source_ = 0
    dist_, prev = solve_shortest_path_dag(graph_, source_)

    print("节点最短距离：")
    for node__ in sorted(dist_):
        print(f"  {node__}: {dist_[node__]}")

    # 重建到节点 3 的路径
    target = 3
    if target in prev:
        path = []
        node = target
        while node in prev:
            path.append(node)
            node = prev[node]
        path.append(source_)
        path.reverse()
        print(f"\n从 {source_} 到 {target} 的最短路径: {path}")
        print(f"距离验证: {dist_[target]}")
    else:
        print(f"节点 {target} 不可达")
