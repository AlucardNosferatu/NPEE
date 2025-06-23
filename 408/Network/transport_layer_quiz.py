import random


class TransportLayerQuizGenerator:
    def __init__(self):
        # 题目类型及其权重
        self.question_types = [
            {"type": "window_size", "weight": 2},  # 窗口大小计算题目权重为2
            {"type": "throughput", "weight": 1}  # 吞吐量计算题目权重为1
        ]
        # 帧编号位数范围
        self.frame_bit_range = (3, 5)
        # RTT范围（毫秒）
        self.rtt_range = (10, 100)
        # 窗口大小范围（帧）
        self.window_size_range = (5, 30)
        # 帧大小范围（字节） - 按照IEEE 802.3标准
        self.frame_size_range = (64, 1518)
        # 带宽范围（Mbps）
        self.bandwidth_base_range = (1, 100)  # 基础范围，实际使用时会根据吞吐量调整

    def generate_question(self):
        """随机选择题目类型并生成相应题目"""
        # 根据权重随机选择题目类型
        question_type = random.choices(
            [q["type"] for q in self.question_types],
            weights=[q["weight"] for q in self.question_types]
        )[0]

        if question_type == "window_size":
            return self._generate_window_size_question()
        else:  # throughput
            return self._generate_throughput_question()

    def _generate_window_size_question(self):
        """生成窗口大小计算题目"""
        # 随机选择协议类型
        protocol = random.choice(["停等协议", "GBN", "SR"])
        # 随机生成帧编号位数
        n = random.randint(*self.frame_bit_range)

        # 计算正确答案
        if protocol == "停等协议":
            answer = 1
            explanation = f"停等协议的发送窗口大小固定为1。"
        elif protocol == "GBN":
            answer = 2 ** n - 1
            explanation = f"GBN协议的发送窗口大小必须小于等于2^{n}-1，即{answer}。"
        else:  # SR
            answer = 2 ** (n - 1)
            explanation = f"SR协议的发送窗口大小必须小于等于2^({n}-1)，即{answer}。"

        question = f"在使用{protocol}的网络中，帧编号使用{n}位二进制数。请计算其发送窗口的最大可能大小。"

        return {
            "type": "window_size",
            "question": question,
            "answer": answer,
            "explanation": explanation
        }

    def _generate_throughput_question(self):
        """生成吞吐量计算题目"""
        # 随机生成基本参数
        rtt = random.randint(*self.rtt_range)
        window_size = random.randint(*self.window_size_range)
        frame_size = random.randint(*self.frame_size_range)

        # 计算理论吞吐量（单位：Mbps）
        theoretical_throughput = (window_size * frame_size * 8) / (rtt / 1000) / (1000 * 1000)

        # 随机决定带宽与吞吐量的关系
        throughput_gt_bandwidth = random.choice([True, False])

        # 根据关系调整带宽
        if throughput_gt_bandwidth:
            # 吞吐量大于带宽的情况
            bandwidth_min = max(self.bandwidth_base_range[0], theoretical_throughput * 0.8)
            bandwidth_max = theoretical_throughput * 0.99
            bandwidth = round(random.uniform(bandwidth_min, bandwidth_max), 2)
            answer = bandwidth  # 实际吞吐量受限于带宽
            explanation = (f"理论吞吐量计算公式为：(窗口大小 × 帧大小 × 8) / RTT = "
                           f"({window_size} × {frame_size} × 8) / {rtt} = {theoretical_throughput:.2f}Mbps。"
                           f"但由于链路带宽限制，实际最大吞吐量为{bandwidth}Mbps。")
        else:
            # 吞吐量小于带宽的情况
            bandwidth_min = theoretical_throughput * 1.01
            bandwidth_max = max(self.bandwidth_base_range[1], theoretical_throughput * 2)
            bandwidth = round(random.uniform(bandwidth_min, bandwidth_max), 2)
            answer = round(theoretical_throughput, 2)  # 实际吞吐量等于理论吞吐量
            explanation = (f"吞吐量计算公式为：(窗口大小 × 帧大小 × 8) / RTT = "
                           f"({window_size} × {frame_size} × 8) / {rtt} = {answer}Mbps。"
                           f"此时链路带宽足够大，不会限制吞吐量。")

        question = (f"已知某网络的RTT为{rtt}ms，带宽为{bandwidth}Mbps，窗口大小为{window_size}帧，"
                    f"帧大小为{frame_size}字节。请计算其最大吞吐量（单位：Mbps）。")

        return {
            "type": "throughput",
            "question": question,
            "answer": answer,
            "explanation": explanation
        }

    def present_quiz(self, num_questions=5):
        """展示一组题目给用户并获取用户答案"""
        print("\n===== 传输层流量控制练习题 =====")
        total_score = 0

        for i in range(num_questions):
            question_data = self.generate_question()
            print(f"\n问题 {i + 1}:")
            print(question_data["question"])

            # 获取用户答案
            user_answer = input("请输入你的答案：")

            # 验证答案格式
            try:
                if question_data["type"] == "window_size":
                    user_answer = int(user_answer)
                else:  # throughput
                    user_answer = float(user_answer)
            except ValueError:
                print(f"答案格式不正确！正确答案是：{question_data['answer']}")
                print(f"解释：{question_data['explanation']}")
                continue

            # 检查答案
            if user_answer == question_data["answer"]:
                print("恭喜，答对了！")
                total_score += 1
            else:
                print(f"答错了！正确答案是：{question_data['answer']}")
                print(f"解释：{question_data['explanation']}")

        # 显示得分
        print(f"\n===== 测试完成 =====")
        print(f"你的得分：{total_score}/{num_questions}")


if __name__ == "__main__":
    quiz_generator = TransportLayerQuizGenerator()
    quiz_generator.present_quiz(3)  # 默认生成3道题
