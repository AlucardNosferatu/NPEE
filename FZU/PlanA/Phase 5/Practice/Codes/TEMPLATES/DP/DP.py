class DP:
    dp = None
    base_cases = None
    depend_func = None
    transit_func = None
    base_check = None

    def __init__(self, transit_func, depend_func, base_cases=None):
        self.transit_func = transit_func
        self.depend_func = depend_func
        self.dp = {}
        self.base_cases = set()
        if base_cases is not None:
            for base_case_state in base_cases.keys():
                self.set_base_case(state=base_case_state, dp_state=base_cases[base_case_state])

    def query(self, state, no_recur=False, from_cal=False):
        if self.base_check is not None:
            res = self.base_check(state)
            if res is not None:
                self.dp[state] = res
                return res
        if state in self.dp.keys() and self.dp[state] is not None:
            return self.dp[state]
        else:
            if no_recur:
                assert (not from_cal)
            return self.calculate(state, no_recur=no_recur)

    def set_base_check(self, base_check=None):
        self.base_check = base_check

    def set_base_case(self, state, dp_state):
        self.base_cases.add(state)
        self.dp[state] = dp_state

    def calculate(self, state, no_recur=False):
        depend_indices: dict = self.depend_func(state=state)
        depend_dp_dict = {}
        for depend_key in depend_indices.keys():
            depend_dp = self.query(
                state=depend_indices[depend_key],
                no_recur=no_recur,
                from_cal=True
            )
            depend_dp_dict[depend_key] = depend_dp
        result = self.transit_func(depend_dp_dict=depend_dp_dict, state=state)
        self.dp[state] = result
        return result
