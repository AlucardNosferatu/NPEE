import random


class DiskSchedulingGenerator:
    def __init__(self):
        # 初始化随机数生成器
        random.seed()

    def generate_question(self):
        """生成随机磁盘调度问题"""
        # 磁道范围
        track_range = (0, 200)

        # 当前磁头位置（在磁道范围内随机选择）
        current_position = random.randint(track_range[0], track_range[1])

        # 请求序列（随机生成5-10个不重复的磁道请求）
        request_count = random.randint(5, 10)
        requests = random.sample(range(track_range[0], track_range[1] + 1), request_count)

        # 确保请求序列中不包含当前磁头位置（如果包含则重新生成）
        while current_position in requests:
            requests = random.sample(range(track_range[0], track_range[1] + 1), request_count)

        return {
            "current_position": current_position,
            "requests": requests,
            "track_range": track_range
        }

    def fcfs(self, current_position, requests):
        """先来先服务(FCFS)算法"""
        # 顺序就是请求到达的顺序
        order = list(requests)
        # 计算总寻道距离
        total_distance = sum(abs(order[i] - (current_position if i == 0 else order[i - 1])) for i in range(len(order)))
        return {
            "order": order,
            "total_distance": total_distance
        }

    def sstf(self, current_position, requests):
        """最短寻道时间优先(SSTF)算法"""
        remaining = list(requests)
        order = []
        current = current_position

        while remaining:
            # 找到距离当前位置最近的请求
            next_track = min(remaining, key=lambda x: abs(x - current))
            order.append(next_track)
            remaining.remove(next_track)
            current = next_track

        # 计算总寻道距离
        total_distance = sum(abs(order[i] - (current_position if i == 0 else order[i - 1])) for i in range(len(order)))
        return {
            "order": order,
            "total_distance": total_distance
        }

    def scan(self, current_position, requests, track_range):
        """扫描(SCAN)算法（电梯算法）"""
        # 将请求排序
        sorted_requests = sorted(requests)

        # 找到当前位置在排序后的请求中的位置
        pos = 0
        while pos < len(sorted_requests) and sorted_requests[pos] < current_position:
            pos += 1

        # 分成两部分：小于等于当前位置的和大于当前位置的
        lower = sorted_requests[:pos]
        upper = sorted_requests[pos:]

        # 假设向磁道号增加的方向移动（向右）
        order = upper + lower[::-1]

        # 如果没有大于当前位置的请求，则直接处理小于的部分（向左移动）
        if not upper:
            order = lower[::-1]

        # 计算总寻道距离
        total_distance = sum(abs(order[i] - (current_position if i == 0 else order[i - 1])) for i in range(len(order)))
        return {
            "order": order,
            "total_distance": total_distance
        }

    def cscan(self, current_position, requests, track_range):
        """循环扫描(CSCAN)算法"""
        # 将请求排序
        sorted_requests = sorted(requests)

        # 找到当前位置在排序后的请求中的位置
        pos = 0
        while pos < len(sorted_requests) and sorted_requests[pos] < current_position:
            pos += 1

        # 分成两部分：小于当前位置的和大于等于当前位置的
        lower = sorted_requests[:pos]  # 所有小于当前位置的请求
        upper = sorted_requests[pos:]  # 所有大于等于当前位置的请求

        # 计算寻道顺序
        order = []
        if upper:
            order.extend(upper)
            if upper[-1] < track_range[1]:
                order.append(track_range[1])
        else:
            order.append(track_range[1])

        if lower:
            order.append(track_range[0])
            order.extend(lower)

        # 使用数学公式优化总寻道距离计算
        L, U = track_range  # 最小和最大磁道号

        # 找到小于当前位置的最大请求（最近小请求磁道）
        if lower:
            S = lower[-1]  # 最近小请求磁道
            total_distance = 2 * (U - L) - (current_position - S)
        else:
            # 没有小于当前位置的请求
            total_distance = (U - current_position) + (U - L)

        return {
            "order": order,
            "total_distance": total_distance
        }

    def solve_question(self, question):
        """解决给定的磁盘调度问题"""
        current_position = question["current_position"]
        requests = question["requests"]
        track_range = question["track_range"]

        fcfs_result = self.fcfs(current_position, requests)
        sstf_result = self.sstf(current_position, requests)
        scan_result = self.scan(current_position, requests, track_range)
        cscan_result = self.cscan(current_position, requests, track_range)

        return {
            "fcfs": fcfs_result,
            "sstf": sstf_result,
            "scan": scan_result,
            "cscan": cscan_result,
            "most_efficient": min(
                [fcfs_result, sstf_result, scan_result, cscan_result],
                key=lambda x: x["total_distance"]
            )
        }

    def generate_question_text(self, question):
        """生成问题文本"""
        return (f"当前磁头位于磁道 {question['current_position']}，磁盘请求序列为："
                f"{question['requests']}，磁盘可用磁道范围为 {question['track_range'][0]}-{question['track_range'][1]}。"
                f"请计算FCFS、SSTF、SCAN和CSCAN算法的寻道顺序和总寻道距离。")

    def generate_answer_text(self, question, solution):
        """生成答案文本"""
        answer = []
        answer.append(f"问题：当前磁头位于磁道 {question['current_position']}，请求序列为 {question['requests']}")
        answer.append("\n答案：")

        algorithms = ["fcfs", "sstf", "scan", "cscan"]
        algorithm_names = {
            "fcfs": "FCFS (先来先服务)",
            "sstf": "SSTF (最短寻道时间优先)",
            "scan": "SCAN (电梯算法)",
            "cscan": "CSCAN (循环扫描)"
        }

        for alg in algorithms:
            result = solution[alg]
            answer.append(f"\n{algorithm_names[alg]}:")
            answer.append(f"  寻道顺序: {result['order']}")
            answer.append(f"  总寻道距离: {result['total_distance']}")

        answer.append("\n最有效率的算法是:")
        most_efficient = solution["most_efficient"]
        for alg in algorithms:
            if solution[alg] == most_efficient:
                answer.append(f"  {algorithm_names[alg]} (总寻道距离: {most_efficient['total_distance']})")

        return "\n".join(answer)


# 示例使用
if __name__ == "__main__":
    generator = DiskSchedulingGenerator()
    question = generator.generate_question()
    solution = generator.solve_question(question)

    print(generator.generate_question_text(question))
    print(generator.generate_answer_text(question, solution))
