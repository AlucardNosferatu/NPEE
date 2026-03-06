from DPBottomUp import DPBottomUp  # Assuming this is in the same directory or package; adjust import as needed


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
            best_prev = greedy_choice(depend_dp_dict=depend_dp_dict, curr_state=state, params=params)
            best_prev_dp = depend_dp_dict[best_prev]
            curr_dp = optimal_substructure(
                prev_dp=best_prev_dp, curr_state=state, params=params
            )
            return curr_dp

        return transit_func
