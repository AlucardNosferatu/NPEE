import random
from math import floor


class BankersAlgorithmGenerator:
    def __init__(self, min_processes=3, max_processes=5, min_resources=3, max_resources=4):
        self.min_processes = min_processes
        self.max_processes = max_processes
        self.min_resources = min_resources
        self.max_resources = max_resources

    def generate_problem(self):
        # 随机确定进程数和资源类型数
        deadlock = random.choice([True, False, False])
        num_processes = random.randint(self.min_processes, self.max_processes)
        num_resources_types = random.randint(self.min_resources, self.max_resources)

        # 生成总资源向量
        total_resources = [random.randint(7, 15) for _ in range(num_resources_types)]

        # 生成Max矩阵和Allocation矩阵，同时确保Available非负
        max_matrix = []
        allocation_matrix = []

        # 预先分配部分资源，但不超过总资源
        allocated_sum = [0] * num_resources_types
        for _ in range(num_processes):
            # 为每个进程生成Max向量，确保不超过总资源
            if deadlock:
                process_max = [random.randint(0, total_resources[i]) for i in range(num_resources_types)]
            else:
                process_max = [
                    random.randint(0, floor(total_resources[i] / num_processes)) for i in range(num_resources_types)
                ]
            max_matrix.append(process_max)

            # 为每个进程生成Allocation向量，确保不超过Max且总和不超过总资源
            process_allocation = []
            for j in range(num_resources_types):
                # 计算该资源类型还能分配的最大量
                max_allocation = min(process_max[j], total_resources[j] - allocated_sum[j])
                allocated = random.randint(0, max_allocation)
                process_allocation.append(allocated)
                allocated_sum[j] += allocated
            allocation_matrix.append(process_allocation)

        # 计算Need矩阵
        need_matrix = []
        for i in range(num_processes):
            need = [max_matrix[i][j] - allocation_matrix[i][j] for j in range(num_resources_types)]
            need_matrix.append(need)

        # 计算Available向量（此时必定非负）
        available = [total_resources[i] - allocated_sum[i] for i in range(num_resources_types)]

        # 随机选择一个进程和资源请求，确保请求合法
        requesting_process = random.randint(0, num_processes - 1)
        request = []
        for j in range(num_resources_types):
            # 请求不能超过Need和Available
            max_request = min(need_matrix[requesting_process][j], available[j])
            if max_request > 0:
                request_val = random.randint(0, max_request)
            else:
                request_val = 0
            request.append(request_val)

        return {
            'num_processes': num_processes,
            'num_resources': num_resources_types,
            'total_resources': total_resources,
            'max_matrix': max_matrix,
            'allocation_matrix': allocation_matrix,
            'need_matrix': need_matrix,
            'available': available,
            'requesting_process': requesting_process,
            'request': request
        }

    @staticmethod
    def is_safe_state(available, max_matrix, allocation_matrix, need_matrix):
        work = available.copy()
        finish = [False] * len(max_matrix)
        safe_sequence = []

        while True:
            found = False
            for i in range(len(max_matrix)):
                if not finish[i] and all(need_matrix[i][j] <= work[j] for j in range(len(work))):
                    # 分配资源
                    for j in range(len(work)):
                        work[j] += allocation_matrix[i][j]
                    finish[i] = True
                    safe_sequence.append(i)
                    found = True
                    break
            if not found:
                break

        if all(finish):
            return True, safe_sequence
        else:
            return False, []

    def solve_problem(self, problem):
        num_resources = problem['num_resources']
        total_resources = problem['total_resources']
        max_matrix = [row.copy() for row in problem['max_matrix']]
        allocation_matrix = [row.copy() for row in problem['allocation_matrix']]
        need_matrix = [row.copy() for row in problem['need_matrix']]
        available = problem['available'].copy()
        requesting_process = problem['requesting_process']
        request = problem['request']

        solution = {
            'initial_state': {
                'total_resources': total_resources,
                'max_matrix': max_matrix,
                'allocation_matrix': allocation_matrix,
                'need_matrix': need_matrix,
                'available': available
            },
            'request': {
                'process': requesting_process,
                'request': request
            }
        }

        # 检查请求是否合法
        request_valid = all(request[j] <= need_matrix[requesting_process][j] for j in range(num_resources)) and all(
            request[j] <= available[j] for j in range(num_resources))

        solution['request_valid'] = request_valid

        if request_valid:
            # 模拟资源分配
            available_sim = [available[j] - request[j] for j in range(num_resources)]
            allocation_sim = [row.copy() for row in allocation_matrix]
            allocation_sim[requesting_process] = [allocation_sim[requesting_process][j] + request[j] for j in
                                                  range(num_resources)]
            need_sim = [row.copy() for row in need_matrix]
            need_sim[requesting_process] = [need_sim[requesting_process][j] - request[j] for j in range(num_resources)]

            solution['simulated_state'] = {
                'available': available_sim,
                'allocation_matrix': allocation_sim,
                'need_matrix': need_sim
            }

            # 检查安全性
            safe, sequence = self.is_safe_state(available_sim, max_matrix, allocation_sim, need_sim)
            solution['safe'] = safe
            solution['safe_sequence'] = sequence if safe else None

        return solution

    @staticmethod
    def format_problem(problem):
        num_processes = problem['num_processes']
        num_res = problem['num_resources']
        total_resources = problem['total_resources']
        available = problem['available']
        max_matrix = problem['max_matrix']
        allocation_matrix = problem['allocation_matrix']
        requesting_process = problem['requesting_process']
        req = problem['request']

        res_names = [chr(ord('A') + i) for i in range(num_res)]

        problem_text = f"""银行家算法题目
================================

系统中有 {num_processes} 个进程（P0, P1, ..., P{num_processes - 1}）和 {num_res} 种资源（{", ".join(res_names)}）。

已知条件如下：
1. 总资源向量: {total_resources} ({", ".join([f"{res_names[i]}: {total_resources[i]}" for i in range(num_res)])})
2. 最大需求矩阵 (Max):
   """

        problem_text += "    " + " ".join([f"{r:>5}" for r in res_names]) + "\n"
        for i in range(num_processes):
            problem_text += f"  P{i}: " + " ".join([f"{val:5}" for val in max_matrix[i]]) + "\n"

        problem_text += "3. 已分配资源矩阵 (Allocation):\n"
        problem_text += "    " + " ".join([f"{r:>5}" for r in res_names]) + "\n"
        for i in range(num_processes):
            problem_text += f"  P{i}: " + " ".join([f"{val:5}" for val in allocation_matrix[i]]) + "\n"

        problem_text += "4. 可用资源向量 (Available): " + ", ".join(
            [f"{res_names[i]}: {available[i]}" for i in range(num_res)]) + "\n"

        problem_text += f"""
现在进程 P{requesting_process} 发出资源请求: {req} ({", ".join([f"{res_names[i]}: {req[i]}" for i in range(num_res)])})

问题:
1. 计算每个进程的需求矩阵 (Need)。
2. 这个请求是否可以被立即批准？请说明理由并展示安全性检查过程。
"""

        return problem_text

    @staticmethod
    def format_solution(solution):
        num_res = len(solution['initial_state']['total_resources'])
        res_names = [chr(ord('A') + i) for i in range(num_res)]

        solution_text = "银行家算法题目解答\n==============================\n\n"

        solution_text += "1. 需求矩阵 (Need) 计算:\n"
        solution_text += "    " + " ".join([f"{r:>5}" for r in res_names]) + "\n"
        for i in range(len(solution['initial_state']['need_matrix'])):
            solution_text += f"  P{i}: " + " ".join(
                [f"{val:5}" for val in solution['initial_state']['need_matrix'][i]]) + "\n"

        solution_text += "\n2. 请求合法性检查:\n"
        p = solution['request']['process']
        req = solution['request']['request']

        req_res = [f'{res_names[i]}: {req[i]}' for i in range(num_res)]
        solution_text += f"   进程 P{p} 请求资源: {req} ({', '.join(req_res)})\n"

        if solution['request_valid']:
            solution_text += "   该请求是合法的（满足 Need 和 Available 约束）。\n\n"

            solution_text += "3. 安全性检查:\n"
            solution_text += "   模拟分配后的可用资源向量: "
            solution_text += ", ".join([f"{res_names[i]}: {solution['simulated_state']['available'][i]}" for i in
                                        range(num_res)]) + "\n\n"

            if solution['safe']:
                solution_text += "   系统处于安全状态，安全序列为: <" + " -> ".join(
                    [f"P{i}" for i in solution['safe_sequence']]) + ">\n\n"
                solution_text += "   因此，可以立即批准该请求。"
            else:
                solution_text += "   系统处于不安全状态，没有找到安全序列。\n\n"
                solution_text += "   因此，不能立即批准该请求，必须让进程 P{process} 等待。"
        else:
            solution_text += "   该请求是非法的，因为：\n"
            if any(req[j] > solution['initial_state']['need_matrix'][p][j] for j in range(num_res)):
                solution_text += "   - 请求超过了进程 P{process} 的最大需求 (Need)。\n"
            if any(req[j] > solution['initial_state']['available'][j] for j in range(num_res)):
                solution_text += "   - 请求超过了当前可用资源 (Available)。\n"
            solution_text += "\n   因此，不能立即批准该请求。"

        return solution_text


def main():
    generator = BankersAlgorithmGenerator()
    problem = generator.generate_problem()
    solution = generator.solve_problem(problem)

    print(generator.format_problem(problem))

    input("按 Enter 键查看答案...")
    print("\n" + "=" * 50 + "\n")
    print(generator.format_solution(solution))


if __name__ == "__main__":
    main()
