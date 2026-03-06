from DPBottomUp import DPBottomUp  # Assuming this is in the same directory or package; adjust import as needed


class GreedyFactory:
    def __init__(
            self,
            prev_candidates_generator,  # 外部：前驱候选生成（01/无界/...）
            feasible,  # 外部：可行前驱判断（贪心：可行性）
            greedy_choice,  # 外部：贪心选择（贪心核心）
            optimal_substructure,  # 外部：最优子结构合并
            initial_state  # 外部：初始状态
    ):
        # 只存「策略函数」，不存任何数据、不存下标、不存params
        self._prev_candidates = prev_candidates_generator
        self._feasible = feasible
        self._greedy_choice = greedy_choice
        self._optimal_substructure = optimal_substructure
        self._initial_state = initial_state

    def depend_func_factory(self, params):
        """
        只做一件事：
        外部给候选 → 过滤出可行前驱
        无遍历、无下标、无idx
        """
        prev_candidates = self._prev_candidates
        feasible = self._feasible

        def depend_func(state):
            prev_states = {}
            # 1. 外部生成候选集
            candidates = prev_candidates(params=params, state=state)
            # 2. 只过滤，不生成候选
            for s in candidates:
                ok = feasible(params=params, curr_state=state, prev_state=s)
                if ok:
                    prev_states[s] = s
            return prev_states

        return depend_func

    def transit_func_factory(self, params):
        """
        贪心转移标准流程：
        可行集 → 贪心选择 → 最优子结构合并
        无下标、无idx、无业务数据
        """
        greedy_choice = self._greedy_choice
        optimal_substructure = self._optimal_substructure
        initial_state = self._initial_state

        def transit_func(depend_dp_dict: dict, state):
            # 边界：无可行前驱 → 外部初始状态
            if not depend_dp_dict:
                return initial_state(params=params, state=state)

            # 1. 贪心选择：选最优前驱
            best_prev = greedy_choice(depend_dp_dict=depend_dp_dict, curr_state=state)
            # 2. 最优子结构：合并出当前最优
            best_prev_dp = depend_dp_dict[best_prev]
            curr_dp = optimal_substructure(
                prev_dp=best_prev_dp, curr_state=state, params=params
            )
            return curr_dp

        return transit_func


class DPGreedy(DPBottomUp):
    """
    Greedy class that inherits from DPBottomUp, integrating the greedy components directly.
    This allows independent usage as a subclass of DPBottomUp, replacing the collaborative GreedyProblem.
    """

    def __init__(
            self,
            prev_candidates_generator,  # Function to generate previous state candidates
            feasible,  # Function to check feasibility of a previous state
            greedy_choice,  # Function to select the best previous state (greedy core)
            optimal_substructure,  # Function to merge the optimal substructure
            initial_state,  # Function to provide initial value when no dependencies
            params,  # Problem-specific parameters (e.g., data arrays, constraints)
            base_cases=None,  # Base cases for DP
            walk_until=None,  # Function to generate states until a condition
            walk_step=None  # Function to generate next states step-by-step
    ):
        depend_func = self.depend_func_factory(
            prev_candidates_generator=prev_candidates_generator,
            feasible=feasible,
            params=params
        )
        transit_func = self.transit_func_factory(
            greedy_choice=greedy_choice,
            optimal_substructure=optimal_substructure,
            initial_state=initial_state,
            params=params
        )
        super().__init__(
            transit_func=transit_func,
            depend_func=depend_func,
            base_cases=base_cases,
            walk_until=walk_until,
            walk_step=walk_step
        )

    @staticmethod
    def depend_func_factory(prev_candidates_generator, feasible, params):
        """
        Factory to create the depend_func, which generates feasible previous states.
        """

        def depend_func(state):
            prev_states = {}
            candidates = prev_candidates_generator(params=params, state=state)
            for s in candidates:
                ok = feasible(params=params, curr_state=state, prev_state=s)
                if ok:
                    prev_states[s] = s
            return prev_states

        return depend_func

    @staticmethod
    def transit_func_factory(greedy_choice, optimal_substructure, initial_state, params):
        """
        Factory to create the transit_func, which performs greedy selection and merges substructure.
        """

        def transit_func(depend_dp_dict: dict, state):
            if not depend_dp_dict:
                return initial_state(params=params, state=state)
            best_prev = greedy_choice(depend_dp_dict=depend_dp_dict, curr_state=state)
            best_prev_dp = depend_dp_dict[best_prev]
            curr_dp = optimal_substructure(
                prev_dp=best_prev_dp, curr_state=state, params=params
            )
            return curr_dp

        return transit_func
