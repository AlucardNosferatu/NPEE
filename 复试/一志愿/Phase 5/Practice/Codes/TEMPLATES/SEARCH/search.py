import copy


class SearchEngine:
    """
    极简通用搜索引擎。
    将搜索流程固定为：处理当前状态 -> 选择下一个状态 -> 检查终止。
    所有对候选状态集的操作（添加、删除、选择）均由外部注入的函数直接完成，
    引擎只负责维护当前状态、候选集和停止标志，并按顺序调用这些函数。
    """

    def __init__(self,
                 process_func,  # (current_state, candidates) -> None   （可修改 candidates，如添加新状态、剪枝）
                 select_func,  # (current_state, candidates) -> next_state （通常从 candidates 中取出一个状态并移除它）
                 stop_cond_func,  # (current_state) -> bool
                 initial_state,
                 initial_candidates):
        """
        :param process_func:     处理当前状态，直接操作 candidates 添加新状态或进行剪枝。
        :param select_func:      从 candidates 中选择下一个状态，通常将其移除并返回。
        :param stop_cond_func:   判断当前状态是否满足终止条件。
        :param initial_state:    起始状态。
        :param initial_candidates: 初始候选状态集（可以是列表、集合、堆等任意容器）。
        """
        self.process_func = process_func
        self.select_func = select_func
        self.stop_cond_func = stop_cond_func
        self.initial_state = initial_state
        self.initial_candidates = initial_candidates
        self.current_state = None
        self.candidates = None
        self.stopped = False
        self.reset()

    def reset(self):
        """重置引擎到初始状态。"""
        self.current_state = copy.deepcopy(self.initial_state)
        self.candidates = copy.deepcopy(self.initial_candidates)
        self.stopped = False

    def step(self):
        """执行一步搜索。"""
        if self.stopped:
            return
        # 1. 处理当前状态：可向 candidates 中添加新状态或进行剪枝
        self.process_func(self.current_state, self.candidates)
        # 2. 从 candidates 中选择下一个状态（通常将其移除）
        self.current_state = self.select_func(self.current_state, self.candidates)
        # 3. 检查是否终止
        if self.stop_cond_func(self.current_state):
            self.stopped = True

    def is_stopped(self):
        return self.stopped
