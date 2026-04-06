from DP import DP


class DPStack(DP):
    def __init__(self, transit_func, depend_func, base_cases=None):
        super().__init__(transit_func, depend_func, base_cases)

    def query(self, state):
        if state in self.dp:
            return self.dp[state]

        stack = [(state, False)]
        while stack:
            cur_state, flag = stack.pop()
            if self._try_cache(cur_state):
                continue
            if not flag:
                self._handle_unready(cur_state, stack)  # 依赖未就绪
            else:
                self._handle_ready(cur_state, stack)  # 依赖已就绪
        return self.dp[state]

    # ---------- 辅助方法 ----------
    def _try_cache(self, state):
        """如果状态已缓存，直接返回 True"""
        if state in self.dp:
            return True
        return False

    def _handle_unready(self, state, stack):
        """首次遇到状态，但依赖可能未就绪：检查base，安排依赖"""
        # 检查是否是基础状态
        if self.base_check is not None:
            base_res = self.base_check(state)
            if base_res is not None:
                self.dp[state] = base_res
                return

        # 获取依赖
        dep_indices = self.depend_func(state=state)

        # 找出缺失的依赖
        missing = [dep for dep in dep_indices.values() if dep not in self.dp]
        if not missing:
            # 所有依赖就绪，立即计算
            dep_dict = {key: self.dp[dep] for key, dep in dep_indices.items()}
            result = self.transit_func(depend_dp_dict=dep_dict, state=state)
            self.dp[state] = result
        else:
            # 依赖缺失：当前状态标记为已就绪待计算（flag=True）重新入栈
            stack.append((state, True))
            # 缺失依赖压栈（后进先出）
            for dep in reversed(missing):
                stack.append((dep, False))

    def _handle_ready(self, state, stack):
        """第二次遇到状态（依赖应已就绪）：计算并缓存"""
        dep_indices = self.depend_func(state=state)
        dep_dict = {}
        for key, dep in dep_indices.items():
            if dep not in self.dp:
                # 异常情况：依赖缺失（极少发生），重新安排
                stack.append((state, False))
                stack.append((dep, False))
                return
            dep_dict[key] = self.dp[dep]
        result = self.transit_func(depend_dp_dict=dep_dict, state=state)
        self.dp[state] = result

    def calculate(self, state):
        # 为保持接口兼容，保留此方法但实际不会调用
        # 新逻辑已内嵌在query中，此方法可留空或调用query
        return self.query(state)
