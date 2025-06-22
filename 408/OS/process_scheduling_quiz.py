import copy
import random


class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=None):
        self.pid = pid  # 进程ID
        self.arrival_time = arrival_time  # 到达时间
        self.burst_time = burst_time  # 执行时间
        self.priority = priority  # 优先级（用于优先级调度）
        self.start_time = None  # 开始执行时间
        self.completion_time = None  # 完成时间
        self.turnaround_time = None  # 周转时间
        self.weighted_turnaround_time = None  # 带权周转时间
        self.remaining_time = burst_time  # 剩余执行时间（用于RR和抢占式SJF）

    def __repr__(self):
        return f"P{self.pid}"


class SchedulingQuestionGenerator:
    def __init__(self):
        self.algorithms = ["FCFS", "SJF", "Priority", "RR"]

    def generate_processes(self, n=4, max_arrival=10, max_burst=10):
        """生成随机进程数据"""
        processes = []
        arrival_times = sorted(random.sample(range(0, max_arrival + 1), n))

        for i in range(n):
            burst_time = random.randint(1, max_burst)
            priority = random.randint(1, 5)  # 优先级1-5，数字越小优先级越高
            processes.append(Process(i + 1, arrival_times[i], burst_time, priority))

        return processes

    def format_process_table(self, processes):
        """格式化进程信息表格"""
        table = "| 进程 | 到达时间 | 执行时间 | 优先级 |\n"
        table += "|------|----------|----------|--------|\n"
        for p in processes:
            table += f"| P{p.pid}  | {p.arrival_time}        | {p.burst_time}        | {p.priority}      |\n"
        return table

    def fcfs(self, processes, verbose=False):
        """先来先服务(FCFS)调度算法"""
        processes = copy.deepcopy(processes)
        # 按到达时间排序，如果到达时间相同则按PID排序
        processes.sort(key=lambda x: (x.arrival_time, x.pid))

        current_time = 0
        schedule_order = []  # 记录调度顺序

        if verbose:
            print("\n===== FCFS调度过程 =====")
            print(f"时间\t当前执行进程\t事件")
            print("--------------------------------")

        for p in processes:
            if current_time < p.arrival_time:
                if verbose:
                    print(f"{current_time} - {p.arrival_time}\tIDLE\tCPU空闲")
                current_time = p.arrival_time

            p.start_time = current_time
            p.completion_time = current_time + p.burst_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.weighted_turnaround_time = p.turnaround_time / p.burst_time

            if verbose:
                print(f"{current_time} - {p.completion_time}\t{p}\t执行完成")

            schedule_order.append(p)  # 记录调度顺序
            current_time = p.completion_time

        return processes, schedule_order

    def sjf_non_preemptive(self, processes, verbose=False):
        """非抢占式短作业优先(SJF)调度算法"""
        processes = copy.deepcopy(processes)
        completed = []
        ready_queue = []
        current_time = 0
        schedule_order = []  # 记录调度顺序

        if verbose:
            print("\n===== 非抢占式SJF调度过程 =====")
            print(f"时间\t当前执行进程\t就绪队列\t事件")
            print("-----------------------------------------------")

        while len(completed) < len(processes):
            # 将已到达的进程加入就绪队列
            for p in processes:
                if p.arrival_time <= current_time and p not in completed and p not in ready_queue:
                    ready_queue.append(p)

            if not ready_queue:
                if verbose:
                    print(f"{current_time}\tIDLE\t{[str(p) for p in ready_queue]}\tCPU空闲")
                current_time += 1
                continue

            # 选择执行时间最短的进程
            ready_queue.sort(key=lambda x: x.burst_time)
            selected = ready_queue.pop(0)

            selected.start_time = current_time
            selected.completion_time = current_time + selected.burst_time
            selected.turnaround_time = selected.completion_time - selected.arrival_time
            selected.weighted_turnaround_time = selected.turnaround_time / selected.burst_time

            if verbose:
                print(
                    f"{current_time} - {selected.completion_time}\t{selected}\t{[str(p) for p in ready_queue]}\t执行完成")

            schedule_order.append(selected)  # 记录调度顺序
            current_time = selected.completion_time
            completed.append(selected)

        # 按PID排序以便展示
        completed.sort(key=lambda x: x.pid)
        return completed, schedule_order

    def sjf_preemptive(self, processes, verbose=False):
        """抢占式短作业优先(SRTF)调度算法"""
        processes = copy.deepcopy(processes)
        completed = []
        ready_queue = []
        current_time = 0
        current_process = None
        schedule_order = []  # 记录调度顺序
        time_chunks = []  # 记录每个时间片的执行情况

        if verbose:
            print("\n===== 抢占式SJF(SRTF)调度过程 =====")
            print(f"时间\t当前执行进程\t就绪队列\t事件")
            print("-----------------------------------------------")

        while len(completed) < len(processes):
            # 将已到达的进程加入就绪队列
            for p in processes:
                if p.arrival_time <= current_time and p not in completed and p not in ready_queue and p != current_process:
                    ready_queue.append(p)

            # 如果当前没有正在执行的进程，或者有更短剩余时间的进程到达
            next_process = None
            if ready_queue:
                ready_queue.sort(key=lambda x: x.remaining_time)
                next_process = ready_queue[0]

            if not current_process or (next_process and next_process.remaining_time < current_process.remaining_time):
                if current_process and current_process.remaining_time > 0:
                    # 确保就绪队列中没有当前进程（避免重复）
                    ready_queue = [p for p in ready_queue if p.pid != current_process.pid]
                    ready_queue.append(current_process)
                    if verbose:
                        print(
                            f"{current_time}\t{current_process}\t{[str(p) for p in ready_queue]}\t被抢占，即将执行: {next_process}")

                if next_process:
                    current_process = ready_queue.pop(0)
                    if current_process.start_time is None:
                        current_process.start_time = current_time
                        if verbose:
                            print(f"{current_time}\t{current_process}\t{[str(p) for p in ready_queue]}\t开始执行")

            if current_process:
                # 执行一个时间单位
                start_time = current_time
                current_process.remaining_time -= 1
                current_time += 1

                # 记录时间片
                time_chunks.append((start_time, current_time, current_process))

                # 检查进程是否完成
                if current_process.remaining_time <= 0:
                    current_process.completion_time = current_time
                    current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
                    current_process.weighted_turnaround_time = current_process.turnaround_time / current_process.burst_time
                    completed.append(current_process)
                    if verbose:
                        next_str = ready_queue[0] if ready_queue else "无"
                        print(
                            f"{current_time}\t{current_process}\t{[str(p) for p in ready_queue]}\t执行完成，即将执行: {next_str}")
                    schedule_order.append(current_process)  # 记录调度顺序
                    current_process = None
            else:
                if verbose:
                    next_str = ready_queue[0] if ready_queue else "无"
                    print(f"{current_time}\tIDLE\t{[str(p) for p in ready_queue]}\tCPU空闲，即将执行: {next_str}")
                current_time += 1

        # 按PID排序以便展示
        completed.sort(key=lambda x: x.pid)
        return completed, schedule_order, time_chunks

    def priority_scheduling(self, processes, verbose=False):
        """优先级调度算法"""
        processes = copy.deepcopy(processes)
        completed = []
        ready_queue = []
        current_time = 0
        schedule_order = []  # 记录调度顺序

        if verbose:
            print("\n===== 优先级调度过程 =====")
            print(f"时间\t当前执行进程\t就绪队列\t事件")
            print("-----------------------------------------------")

        while len(completed) < len(processes):
            # 将已到达的进程加入就绪队列
            for p in processes:
                if p.arrival_time <= current_time and p not in completed and p not in ready_queue:
                    ready_queue.append(p)

            if not ready_queue:
                if verbose:
                    print(f"{current_time}\tIDLE\t{[str(p) for p in ready_queue]}\tCPU空闲")
                current_time += 1
                continue

            # 选择优先级最高的进程（数字越小优先级越高）
            ready_queue.sort(key=lambda x: x.priority)
            selected = ready_queue.pop(0)

            selected.start_time = current_time
            selected.completion_time = current_time + selected.burst_time
            selected.turnaround_time = selected.completion_time - selected.arrival_time
            selected.weighted_turnaround_time = selected.turnaround_time / selected.burst_time

            if verbose:
                print(
                    f"{current_time} - {selected.completion_time}\t{selected}\t{[str(p) for p in ready_queue]}\t执行完成")

            schedule_order.append(selected)  # 记录调度顺序
            current_time = selected.completion_time
            completed.append(selected)

        # 按PID排序以便展示
        completed.sort(key=lambda x: x.pid)
        return completed, schedule_order

    def round_robin(self, processes, time_quantum=2, verbose=False):
        """时间片轮转(RR)调度算法"""
        processes = copy.deepcopy(processes)
        completed = []
        ready_queue = []
        current_time = 0
        time_quantum_count = 0
        current_process = None
        schedule_order = []  # 记录调度顺序
        time_chunks = []  # 记录每个时间片的执行情况

        if verbose:
            print(f"\n===== 时间片大小为{time_quantum}的RR调度过程 =====")
            print(f"时间\t当前执行进程\t就绪队列\t剩余时间\t事件")
            print("--------------------------------------------------------")

        while len(completed) < len(processes):
            # 将已到达的进程加入就绪队列
            for p in processes:
                if p.arrival_time <= current_time and p not in completed and p not in ready_queue and p != current_process:
                    ready_queue.append(p)

            # 如果当前没有正在执行的进程，从就绪队列中选择
            next_process = ready_queue[0] if ready_queue else None
            if not current_process and ready_queue:
                current_process = ready_queue.pop(0)
                if current_process.start_time is None:
                    current_process.start_time = current_time
                    if verbose:
                        next_str = ready_queue[0] if ready_queue else "无"
                        print(
                            f"{current_time}\t{current_process}\t{[str(p) for p in ready_queue]}\t{current_process.remaining_time}\t开始执行，下一个: {next_str}")
                time_quantum_count = 0

            if current_process:
                # 执行一个时间单位
                start_time = current_time
                current_process.remaining_time -= 1
                current_time += 1
                time_quantum_count += 1

                # 记录时间片
                time_chunks.append((start_time, current_time, current_process))

                # 检查进程是否完成
                if current_process.remaining_time <= 0:
                    current_process.completion_time = current_time
                    current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
                    current_process.weighted_turnaround_time = current_process.turnaround_time / current_process.burst_time
                    completed.append(current_process)
                    next_str = ready_queue[0] if ready_queue else "无"
                    if verbose:
                        print(
                            f"{current_time}\t{current_process}\t{[str(p) for p in ready_queue]}\t0\t执行完成，即将执行: {next_str}")
                    schedule_order.append(current_process)  # 记录调度顺序
                    current_process = None
                    time_quantum_count = 0
                # 检查时间片是否用完
                elif time_quantum_count == time_quantum:
                    if ready_queue:
                        # 确保就绪队列中没有当前进程（避免重复）
                        ready_queue = [p for p in ready_queue if p.pid != current_process.pid]
                        ready_queue.append(current_process)
                        next_str = ready_queue[0]
                        if verbose:
                            print(
                                f"{current_time}\t{current_process}\t{[str(p) for p in ready_queue]}\t{current_process.remaining_time}\t时间片用完，加入队列尾部，即将执行: {next_str}")
                    else:
                        next_str = "无"
                        if verbose:
                            print(
                                f"{current_time}\t{current_process}\t{[str(p) for p in ready_queue]}\t{current_process.remaining_time}\t时间片用完，但就绪队列为空，即将执行: {next_str}")
                    current_process = None
                    time_quantum_count = 0
            else:
                next_str = ready_queue[0] if ready_queue else "无"
                if verbose:
                    print(f"{current_time}\tIDLE\t{[str(p) for p in ready_queue]}\t-\tCPU空闲，即将执行: {next_str}")
                current_time += 1

        # 按PID排序以便展示
        completed.sort(key=lambda x: x.pid)
        return completed, schedule_order, time_chunks

    def calculate_cpu_utilization(self, processes):
        """计算CPU利用率"""
        total_burst_time = sum(p.burst_time for p in processes)
        completion_time = max(p.completion_time for p in processes)
        return (total_burst_time / completion_time) * 100

    def calculate_average_turnaround_time(self, processes):
        """计算平均周转时间"""
        return sum(p.turnaround_time for p in processes) / len(processes)

    def calculate_average_weighted_turnaround_time(self, processes):
        """计算平均带权周转时间"""
        return sum(p.weighted_turnaround_time for p in processes) / len(processes)

    def generate_question(self, verbose=False):
        """生成完整的进程调度问题及答案"""
        n = random.randint(3, 5)  # 随机生成3-5个进程
        processes = self.generate_processes(n)
        time_quantum = random.randint(1, 3)  # 随机时间片大小

        # 生成问题描述
        question = "### 进程调度算法计算题\n\n"
        question += "给定以下进程的到达时间、执行时间和优先级：\n\n"
        question += self.format_process_table(processes)
        question += "\n请计算：\n"
        question += "1. 先来先服务(FCFS)调度算法的调度顺序、每个进程的周转时间、带权周转时间，以及CPU利用率和平均周转时间。\n"
        question += "2. 非抢占式短作业优先(SJF)调度算法的调度顺序、每个进程的周转时间、带权周转时间，以及CPU利用率和平均周转时间。\n"
        question += "3. 抢占式短作业优先(SRTF)调度算法的调度顺序、每个进程的周转时间、带权周转时间，以及CPU利用率和平均周转时间。\n"
        question += "4. 优先级调度算法的调度顺序、每个进程的周转时间、带权周转时间，以及CPU利用率和平均周转时间。\n"
        question += f"5. 时间片大小为{time_quantum}的时间片轮转(RR)调度算法的调度顺序、每个进程的周转时间、带权周转时间，以及CPU利用率和平均周转时间。\n"
        question += "6. 比较上述五种调度算法的平均周转时间和CPU利用率，哪种算法效率最高？\n\n"

        # 计算答案
        fcfs_processes, fcfs_order = self.fcfs(copy.deepcopy(processes), verbose)
        sjf_np_processes, sjf_np_order = self.sjf_non_preemptive(copy.deepcopy(processes), verbose)
        sjf_p_processes, sjf_p_order, sjf_p_chunks = self.sjf_preemptive(copy.deepcopy(processes), verbose)
        priority_processes, priority_order = self.priority_scheduling(copy.deepcopy(processes), verbose)
        rr_processes, rr_order, rr_chunks = self.round_robin(copy.deepcopy(processes), time_quantum, verbose)

        # 生成答案
        answer = "### 答案\n\n"

        # FCFS答案
        answer += "#### 1. 先来先服务(FCFS)调度算法\n\n"
        answer += f"调度顺序：{', '.join(str(p) for p in fcfs_order)}\n\n"
        answer += "| 进程 | 完成时间 | 周转时间 | 带权周转时间 |\n"
        answer += "|------|----------|----------|--------------|\n"
        for p in fcfs_processes:
            answer += f"| P{p.pid}  | {p.completion_time}        | {p.turnaround_time}        | {p.weighted_turnaround_time:.2f}        |\n"
        answer += f"\nCPU利用率：{self.calculate_cpu_utilization(fcfs_processes):.2f}%\n"
        answer += f"平均周转时间：{self.calculate_average_turnaround_time(fcfs_processes):.2f}\n\n"

        # SJF非抢占式答案
        answer += "#### 2. 非抢占式短作业优先(SJF)调度算法\n\n"
        answer += f"调度顺序：{', '.join(str(p) for p in sjf_np_order)}\n\n"
        answer += "| 进程 | 完成时间 | 周转时间 | 带权周转时间 |\n"
        answer += "|------|----------|----------|--------------|\n"
        for p in sjf_np_processes:
            answer += f"| P{p.pid}  | {p.completion_time}        | {p.turnaround_time}        | {p.weighted_turnaround_time:.2f}        |\n"
        answer += f"\nCPU利用率：{self.calculate_cpu_utilization(sjf_np_processes):.2f}%\n"
        answer += f"平均周转时间：{self.calculate_average_turnaround_time(sjf_np_processes):.2f}\n\n"

        # SJF抢占式答案
        answer += "#### 3. 抢占式短作业优先(SRTF)调度算法\n\n"
        # 构建详细的调度顺序（显示每个时间片）
        detailed_schedule = []
        current_p = None
        for start, end, p in sjf_p_chunks:
            if p != current_p:
                if current_p is not None:
                    detailed_schedule[-1][2] = start  # 更新上一个进程的结束时间
                detailed_schedule.append([p, start, end])
                current_p = p
            else:
                detailed_schedule[-1][2] = end  # 更新当前进程的结束时间

        schedule_str = ", ".join([f"{p}({start}-{end})" for p, start, end in detailed_schedule])
        answer += f"调度顺序：{schedule_str}\n\n"
        answer += "| 进程 | 完成时间 | 周转时间 | 带权周转时间 |\n"
        answer += "|------|----------|----------|--------------|\n"
        for p in sjf_p_processes:
            answer += f"| P{p.pid}  | {p.completion_time}        | {p.turnaround_time}        | {p.weighted_turnaround_time:.2f}        |\n"
        answer += f"\nCPU利用率：{self.calculate_cpu_utilization(sjf_p_processes):.2f}%\n"
        answer += f"平均周转时间：{self.calculate_average_turnaround_time(sjf_p_processes):.2f}\n\n"

        # 优先级调度答案
        answer += "#### 4. 优先级调度算法\n\n"
        answer += f"调度顺序：{', '.join(str(p) for p in priority_order)}\n\n"
        answer += "| 进程 | 完成时间 | 周转时间 | 带权周转时间 |\n"
        answer += "|------|----------|----------|--------------|\n"
        for p in priority_processes:
            answer += f"| P{p.pid}  | {p.completion_time}        | {p.turnaround_time}        | {p.weighted_turnaround_time:.2f}        |\n"
        answer += f"\nCPU利用率：{self.calculate_cpu_utilization(priority_processes):.2f}%\n"
        answer += f"平均周转时间：{self.calculate_average_turnaround_time(priority_processes):.2f}\n\n"

        # RR调度答案
        answer += f"#### 5. 时间片大小为{time_quantum}的时间片轮转(RR)调度算法\n\n"
        # 构建详细的调度顺序（显示每个时间片）
        detailed_schedule = []
        current_p = None
        for start, end, p in rr_chunks:
            if p != current_p:
                if current_p is not None:
                    detailed_schedule[-1][2] = start  # 更新上一个进程的结束时间
                detailed_schedule.append([p, start, end])
                current_p = p
            else:
                detailed_schedule[-1][2] = end  # 更新当前进程的结束时间

        schedule_str = ", ".join([f"{p}({start}-{end})" for p, start, end in detailed_schedule])
        answer += f"调度顺序：{schedule_str}\n\n"
        answer += "| 进程 | 完成时间 | 周转时间 | 带权周转时间 |\n"
        answer += "|------|----------|----------|--------------|\n"
        for p in rr_processes:
            answer += f"| P{p.pid}  | {p.completion_time}        | {p.turnaround_time}        | {p.weighted_turnaround_time:.2f}        |\n"
        answer += f"\nCPU利用率：{self.calculate_cpu_utilization(rr_processes):.2f}%\n"
        answer += f"平均周转时间：{self.calculate_average_turnaround_time(rr_processes):.2f}\n\n"

        # 比较答案
        answer += "#### 6. 算法效率比较\n\n"
        algorithms = ["FCFS", "SJF(非抢占)", "SJF(抢占)", "优先级调度", f"RR(时间片={time_quantum})"]
        avg_turnaround_times = [
            self.calculate_average_turnaround_time(fcfs_processes),
            self.calculate_average_turnaround_time(sjf_np_processes),
            self.calculate_average_turnaround_time(sjf_p_processes),
            self.calculate_average_turnaround_time(priority_processes),
            self.calculate_average_turnaround_time(rr_processes)
        ]
        cpu_utilizations = [
            self.calculate_cpu_utilization(fcfs_processes),
            self.calculate_cpu_utilization(sjf_np_processes),
            self.calculate_cpu_utilization(sjf_p_processes),
            self.calculate_cpu_utilization(priority_processes),
            self.calculate_cpu_utilization(rr_processes)
        ]

        answer += "| 算法 | 平均周转时间 | CPU利用率 |\n"
        answer += "|------|--------------|-----------|\n"
        for i in range(len(algorithms)):
            answer += f"| {algorithms[i]} | {avg_turnaround_times[i]:.2f} | {cpu_utilizations[i]:.2f}% |\n"

        min_avg_turnaround_idx = avg_turnaround_times.index(min(avg_turnaround_times))
        max_cpu_utilization_idx = cpu_utilizations.index(max(cpu_utilizations))

        answer += "\n**结论**：\n"
        answer += f"- **平均周转时间最短**的算法：{algorithms[min_avg_turnaround_idx]}\n"
        answer += f"- **CPU利用率最高**的算法：{algorithms[max_cpu_utilization_idx]}\n"
        answer += "- 通常来说，平均周转时间越短，算法效率越高。因此，在本题中，效率最高的算法是："
        answer += f"{algorithms[min_avg_turnaround_idx]}。\n"

        return question, answer


if __name__ == "__main__":
    generator = SchedulingQuestionGenerator()
    # 直接在代码中指定是否启用verbose模式
    question, answer = generator.generate_question(verbose=True)  # 设置为True或False
    print(question)
    print(answer)
