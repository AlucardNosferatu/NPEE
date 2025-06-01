import random


class PipelinePerformanceAnalyzer:
    def __init__(self):
        # 定义流水线段数范围
        self.stage_range = (4, 6)
        # 定义指令数量范围
        self.instruction_range = (5, 15)
        # 定义各段时间单位范围（ns）
        self.time_unit_range = (1, 5)
        # 定义数据冲突类型及其影响因子
        self.hazards = {
            "RAW": {"probability": 0.6, "stall_cycles": (1, 2)},
            "WAR": {"probability": 0.3, "stall_cycles": (1, 1)},
            "WAW": {"probability": 0.1, "stall_cycles": (1, 1)}
        }

    def generate_problem(self):
        """生成流水线性能分析题目"""
        # 随机生成流水线段数
        num_stages = random.randint(*self.stage_range)
        # 随机生成各段时间
        stage_times = [random.randint(*self.time_unit_range) for _ in range(num_stages)]
        # 随机生成指令数量
        num_instructions = random.randint(*self.instruction_range)
        # 随机决定是否有数据冲突
        has_hazard = random.choice([True, False])
        hazard_info = None

        if has_hazard:
            # 随机选择一种数据冲突类型
            hazard_type = random.choice(list(self.hazards.keys()))
            # 随机生成冲突指令对数量
            num_hazard_pairs = random.randint(1, max(1, num_instructions // 3))
            # 随机生成冲突位置和停顿周期
            hazard_pairs = []
            for _ in range(num_hazard_pairs):
                if num_instructions > 1:
                    i = random.randint(1, num_instructions - 1)
                    j = random.randint(i + 1, min(i + 3, num_instructions))
                    stall = random.randint(*self.hazards[hazard_type]["stall_cycles"])
                    hazard_pairs.append((i, j, stall))

            hazard_info = {
                "type": hazard_type,
                "pairs": hazard_pairs
            }

        return {
            "num_stages": num_stages,
            "stage_times": stage_times,
            "num_instructions": num_instructions,
            "hazard_info": hazard_info
        }

    @staticmethod
    def calculate_performance(problem):
        num_stages = problem["num_stages"]
        stage_times = problem["stage_times"]
        num_instructions = problem["num_instructions"]
        hazard_info = problem["hazard_info"]
        clock_cycle = max(stage_times)
        theoretical_time = sum(stage_times) + (num_instructions - 1) * clock_cycle
        total_stalls = 0
        if hazard_info:
            for pair in hazard_info["pairs"]:
                i, j, stall = pair
                total_stalls += stall
        actual_time = theoretical_time + total_stalls * clock_cycle
        throughput = num_instructions / actual_time
        speedup = (num_instructions * sum(stage_times)) / actual_time
        # 修改前
        # efficiency = (num_instructions * sum(stage_times)) / (actual_time * num_stages)
        # 修改后
        efficiency = (num_instructions * sum(stage_times)) / (theoretical_time * num_stages)
        return {
            "clock_cycle": clock_cycle,
            "theoretical_time": theoretical_time,
            "actual_time": actual_time,
            "total_stalls": total_stalls,
            "throughput": throughput,
            "speedup": speedup,
            "efficiency": efficiency
        }

    @staticmethod
    def format_problem(problem):
        """格式化问题描述"""
        stage_times_str = ", ".join([f"{t}ns" for t in problem["stage_times"]])
        hazard_info = problem["hazard_info"]

        problem_text = f"""
考研408指令流水线性能分析题目：

已知某指令流水线分为{problem["num_stages"]}段，各段执行时间分别为：{stage_times_str}。
现在有{problem["num_instructions"]}条指令需要执行。

请计算：
1. 流水线的时钟周期是多少？
2. 不考虑数据冲突的情况下，执行完所有指令需要的总时间是多少？
3. 考虑数据冲突的情况下，执行完所有指令需要的总时间是多少？
4. 流水线的实际吞吐率（单位：条指令/ns）是多少？
5. 流水线的加速比是多少？
6. 流水线的效率是多少？
"""

        if hazard_info:
            hazard_text = f"\n附加条件：存在{hazard_info['type']}数据冲突，具体冲突情况如下：\n"
            for i, pair in enumerate(hazard_info["pairs"]):
                inst_i, inst_j, stall = pair
                hazard_text += f"  冲突{i + 1}：指令{inst_i}和指令{inst_j}之间存在{hazard_info['type']}冲突，导致{stall}个时钟周期的停顿。\n"
            problem_text += hazard_text

        return problem_text

    @staticmethod
    def format_solution(problem, solution):
        """格式化答案"""
        stage_times = problem["stage_times"]
        num_instructions = problem["num_instructions"]
        hazard_info = problem["hazard_info"]

        solution_text = f"""
解答：

1. 流水线的时钟周期：
   时钟周期等于各段执行时间的最大值，即 max({', '.join(map(str, stage_times))}) = {solution['clock_cycle']}ns

2. 不考虑数据冲突的总时间：
   总时间 = 第一条指令耗时 + (n - 1) × 时钟周期
          = {sum(stage_times)} + ({num_instructions} - 1) × {solution['clock_cycle']}
          = {solution['theoretical_time']}ns

3. 考虑数据冲突的总时间：
"""

        if hazard_info:
            solution_text += f"   存在{hazard_info['type']}数据冲突，共导致{solution['total_stalls']}个时钟周期的停顿\n"
        else:
            solution_text += "   不存在数据冲突，因此总时间等于理论时间\n"

        solution_text += f"""
   总时间 = 理论时间 + 停顿时间
          = {solution['theoretical_time']} + {solution['total_stalls']} × {solution['clock_cycle']}
          = {solution['actual_time']}ns

4. 实际吞吐率：
   吞吐率 = 指令数 / 实际总时间
          = {num_instructions} / {solution['actual_time']}
          ≈ {solution['throughput']:.6f} 条指令/ns

5. 加速比：
   非流水线执行时间 = 指令数 × 各段时间之和
                   = {num_instructions} × {sum(stage_times)}
                   = {num_instructions * sum(stage_times)}ns
   加速比 = 非流水线执行时间 / 实际总时间
          = {num_instructions * sum(stage_times)} / {solution['actual_time']}
          ≈ {solution['speedup']:.6f}

6. 效率：
   效率 = (指令数 × 各段时间之和) / (实际总时间 × 段数)
          = ({num_instructions} × {sum(stage_times)}) / ({solution['actual_time']} × {problem["num_stages"]})
          ≈ {solution['efficiency']:.6f} 或 {solution['efficiency'] * 100:.2f}%
"""
        return solution_text


def main():
    analyzer = PipelinePerformanceAnalyzer()
    problem = analyzer.generate_problem()
    solution = analyzer.calculate_performance(problem)

    print(analyzer.format_problem(problem))
    print(analyzer.format_solution(problem, solution))


if __name__ == "__main__":
    main()
