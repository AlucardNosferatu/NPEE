import copy


# 自定义异常
class NotApplicable(Exception):
    """算法主动报告不适用，应尝试下一个算法"""
    pass


class NoApplicableAlgorithm(Exception):
    """所有算法均不适用"""
    pass


class AlgorithmUnit:
    def __init__(self, func, pre_condition=None, post_condition=None, name=None):
        self.func = func
        self.pre_condition = pre_condition
        self.post_condition = post_condition
        self.name = name or func.__name__


class AlgorithmChain:
    def __init__(self, algorithms):
        self.algorithms = algorithms

    def run(self, input_data):
        for algo in self.algorithms:
            try:
                # 前置检查
                if algo.pre_condition and not algo.pre_condition(input_data):
                    print(f"{algo.name} 前置条件不满足，跳过")
                    continue
                # 执行算法（深拷贝输入，保证隔离）
                data_copy = copy.deepcopy(input_data)
                result = algo.func(data_copy)
                # 后置检查
                if algo.post_condition and not algo.post_condition(input_data, result):
                    print(f"{algo.name} 后置条件失败，结果无效")
                    continue
                print(f"{algo.name} 成功，结果: {result}")
                return result
            except NotApplicable:
                print(f"{algo.name} 主动报告不适用，尝试下一个")
                continue
            except Exception as e:
                print(f"{algo.name} 发生其他异常: {e}，终止")
                raise
        raise NoApplicableAlgorithm("所有算法都不适用")
