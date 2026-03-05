from collections import deque, defaultdict

from DP import DP


# Bottom-Up
class DPBottomUp(DP):
    walk_until = None
    walk_step = None

    def __init__(self, transit_func, depend_func, base_cases=None, walk_until=None, walk_step=None):
        super().__init__(transit_func, depend_func, base_cases)
        self.walk_until = walk_until
        self.walk_step = walk_step

    def growth(self, until):
        assert (self.walk_until is not None or self.walk_step is not None)
        order: list[int] = self.Kahn_until(until=until)
        res = {}
        for state in order:
            dp_state = self.query(state=state, no_recur=True)
            res[state] = dp_state
        return res

    # noinspection PyPep8Naming
    def Kahn_until(self, until):
        if self.walk_until is not None:
            states = self.walk_until(until=until)
        elif self.walk_step is not None:
            states = self.walk_step_until(until=until)
        else:
            raise AttributeError('how did you get here')
        order = self.Kahn_states(states=states)
        return order

    # noinspection PyPep8Naming
    def Kahn_states_old(self, states):
        order = []
        prev_states = {}
        for state in states:
            prev_states[state] = self.get_prev_states(state=state)
        prev_states = list(prev_states.items())
        while len(prev_states) > 0:
            prev_states = sorted(prev_states, key=lambda x: -len(x[1]))
            state = prev_states.pop()
            assert (len(state[1]) == 0)
            order.append(state[0])
            [s[1].remove(state[0]) for s in prev_states if state[0] in s[1]]
        return order

    # noinspection PyPep8Naming
    def Kahn_states(self, states):
        in_degree = {}
        graph = defaultdict(list)  # 邻接表：依赖 → 后继
        for s in states:
            deps = self.get_prev_states(s)  # 返回依赖集合
            in_degree[s] = len(deps)
            for dep in deps:
                graph[dep].append(s)
        q = deque([s for s in states if in_degree[s] == 0])
        order = []
        while q:
            u = q.popleft()
            order.append(u)
            for v in graph[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    q.append(v)
        if len(order) != len(states):
            raise ValueError("存在环")
        return order

    def walk_step_until(self, until, warning_size=100):
        def enq_and_record(s, q, r):
            q.append(s)
            r.add(s)
            return None

        next_states_func = self.walk_step
        res = set()
        queue = deque()
        for initial_state in self.base_cases:
            queue.append(initial_state)
            res.add(initial_state)
        while until not in res:
            current_state = queue.popleft()
            next_states = next_states_func(state=current_state)
            [enq_and_record(s=next_state, q=queue, r=res) for next_state in next_states if next_state not in res]
            assert (len(res) <= warning_size)
        return res

    def get_prev_states(self, state):
        base = False
        if self.base_check is not None:
            res = self.base_check(state)
            if res is None:
                base = True
        if state in self.base_cases:
            base = True
        if base:
            in_degree = set()
        else:
            depend_indices: dict = self.depend_func(state=state)
            in_degree = set(depend_indices.values())
        return in_degree
