import random


class DiskSchedulingGenerator:
    def __init__(self):
        # 初始化随机数生成器
        random.seed()

    @staticmethod
    def generate_question():
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

    @staticmethod
    def fcfs(current_position, requests):
        """先来先服务(FCFS)算法"""
        # 顺序就是请求到达的顺序
        order = list(requests)
        # 计算总寻道距离
        total_distance = sum(abs(order[i] - (current_position if i == 0 else order[i - 1])) for i in range(len(order)))
        return {
            "order": order,
            "total_distance": total_distance
        }

    @staticmethod
    def sstf(current_position, requests):
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

    @staticmethod
    def scan(current_position, requests, track_range):
        """扫描(SCAN)算法（电梯算法）"""
        if not requests:
            return {"order": [], "total_distance": 0}

        # 将请求排序
        sorted_requests = sorted(requests)

        # 找到当前位置在排序后的请求中的位置
        pos = 0
        while pos < len(sorted_requests) and sorted_requests[pos] < current_position:
            pos += 1

        # 分成两部分：小于当前位置的和大于等于当前位置的
        lower = sorted_requests[:pos]
        upper = sorted_requests[pos:]

        # 假设向磁道号增加的方向移动（向右）
        order = []
        if upper:
            order.extend(upper)
            # 移动到磁盘最大磁道（无论是否有请求）
            if upper[-1] < track_range[1]:
                order.append(track_range[1])
        else:
            # 如果没有大于当前位置的请求，直接移动到磁盘最大磁道
            order.append(track_range[1])

        # 反向移动，处理所有小于当前位置的请求
        if lower:
            order.extend(reversed(lower))

        # 计算总寻道距离
        total_distance = sum(abs(order[i] - (current_position if i == 0 else order[i - 1])) for i in range(len(order)))
        return {
            "order": order,
            "total_distance": total_distance
        }

    @staticmethod
    def cscan(current_position, requests, track_range):
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
        l, u = track_range  # 最小和最大磁道号

        # 找到小于当前位置的最大请求（最近小请求磁道）
        if lower:
            s = lower[-1]  # 最近小请求磁道
            total_distance = 2 * (u - l) - (current_position - s)
        else:
            # 没有小于当前位置的请求
            total_distance = (u - current_position) + (u - l)

        return {
            "order": order,
            "total_distance": total_distance
        }

    @staticmethod
    def look(current_position, requests):
        """LOOK调度算法"""
        if not requests:
            return {"order": [], "total_distance": 0}

        # 将请求排序
        sorted_requests = sorted(requests)

        # 找到当前位置在排序后的请求中的位置
        pos = 0
        while pos < len(sorted_requests) and sorted_requests[pos] < current_position:
            pos += 1

        # 分成两部分：小于当前位置的和大于等于当前位置的
        lower = sorted_requests[:pos]
        upper = sorted_requests[pos:]

        # 假设向磁道号增加的方向移动（向右）
        # LOOK算法只移动到最远的请求，而不是磁盘边界
        if upper:
            order = upper + lower[::-1]
        else:
            order = lower[::-1]

        # 计算总寻道距离
        total_distance = sum(abs(order[i] - (current_position if i == 0 else order[i - 1])) for i in range(len(order)))
        return {
            "order": order,
            "total_distance": total_distance
        }

    @staticmethod
    def clook(current_position, requests):
        """CLOOK调度算法"""
        if not requests:
            return {"order": [], "total_distance": 0}
        # 将请求排序
        sorted_requests = sorted(requests)

        # 找到当前位置在排序后的请求中的位置
        pos = 0
        while pos < len(sorted_requests) and sorted_requests[pos] < current_position:
            pos += 1

        # 分成两部分：小于当前位置的和大于等于当前位置的
        lower = sorted_requests[:pos]
        upper = sorted_requests[pos:]

        # CLOOK算法只移动到最远的请求，然后直接回到最开始的请求
        if upper:
            order = upper + lower
        else:
            # 如果没有大于等于当前位置的请求，先处理所有小于的请求
            order = lower
            # 然后从最大请求直接回到最小请求（循环）
            if lower:
                total_distance = (lower[-1] - current_position) + (lower[-1] - lower[0])
                total_distance += sum(abs(lower[i] - lower[i - 1]) for i in range(1, len(lower)))
                return {
                    "order": order,
                    "total_distance": total_distance
                }

        # 计算总寻道距离
        total_distance = sum(abs(order[i] - (current_position if i == 0 else order[i - 1])) for i in range(len(order)))
        if upper and lower:
            # 从最大请求直接回到最小请求的跳转距离
            total_distance += (upper[-1] - lower[0])

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
        look_result = self.look(current_position, requests)
        clook_result = self.clook(current_position, requests)

        return {
            "fcfs": fcfs_result,
            "sstf": sstf_result,
            "scan": scan_result,
            "cscan": cscan_result,
            "look": look_result,
            "clook": clook_result,
            "most_efficient": min(
                [fcfs_result, sstf_result, scan_result, cscan_result, look_result, clook_result],
                key=lambda x: x["total_distance"]
            )
        }

    @staticmethod
    def generate_question_text(question):
        """生成问题文本"""
        return (f"当前磁头位于磁道 {question['current_position']}，磁盘请求序列为："
                f"{question['requests']}，磁盘可用磁道范围为 {question['track_range'][0]}-{question['track_range'][1]}。"
                f"请计算FCFS、SSTF、SCAN、CSCAN、LOOK和CLOOK算法的寻道顺序和总寻道距离。")

    @staticmethod
    def generate_answer_text(question, solution):
        """生成答案文本"""
        answer = [f"问题：当前磁头位于磁道 {question['current_position']}，请求序列为 {question['requests']}", "\n答案："]

        algorithms = ["fcfs", "sstf", "scan", "cscan", "look", "clook"]
        algorithm_names = {
            "fcfs": "FCFS (先来先服务)",
            "sstf": "SSTF (最短寻道时间优先)",
            "scan": "SCAN (电梯算法)",
            "cscan": "CSCAN (循环扫描)",
            "look": "LOOK",
            "clook": "CLOOK"
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
    question_ = generator.generate_question()
    solution_ = generator.solve_question(question_)

    print(generator.generate_question_text(question_))
    print(generator.generate_answer_text(question_, solution_))
