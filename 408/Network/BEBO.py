import random
import argparse

class BackoffQuestionGenerator:
    """
    二进制指数退避算法考题生成器 (适配408计算机网络考点)
    根据CSMA/CD协议和408真题设计，生成选择题和填空题。
    """
    
    def __init__(self, slot_time=51.2, max_collisions=16, k_limit=10):
        """
        初始化生成器参数。
        :param slot_time: 争用期时长（微秒），10BaseT以太网默认为51.2μs[citation:5]
        :param max_collisions: 最大重传次数，默认16次[citation:10]
        :param k_limit: 退避指数k的上限，默认10[citation:4]
        """
        self.slot_time = slot_time
        self.max_collisions = max_collisions
        self.k_limit = k_limit
        # 预定义一些数据帧编号，用于丰富题干
        self.frame_id_pool = [f"Frame_{i}" for i in range(1, 11)] + ["数据帧A", "帧X", "数据分组P"]
    
    def generate_params(self):
        """生成随机题目参数：冲突次数和帧编号。"""
        collision_count = random.randint(0, self.max_collisions)  # 冲突次数 0~16
        frame_id = random.choice(self.frame_id_pool)
        return collision_count, frame_id
    
    def _calculate_backoff_window(self, k):
        """
        计算退避窗口大小。
        :param k: min(冲突次数, 10)[citation:4]
        :return: 退避窗口大小 (2^k - 1)，k>10时为1023[citation:4]
        """
        effective_k = min(k, self.k_limit)
        return (1 << effective_k) - 1  # 等价于 2^effective_k - 1
    
    def _generate_distractors(self, correct_value, k):
        """
        为选择题生成3个符合指数逻辑的干扰项[citation:5]。
        :param correct_value: 正确答案
        :param k: 当前冲突次数（用于生成邻近干扰）
        """
        distractors = set()
        # 策略1：使用邻近的指数值（如正确为2^3-1=7，干扰为2^2-1=3, 2^4-1=15）
        base_values = []
        if k > 1:
            base_values.append((1 << (k-1)) - 1)  # 2^(k-1)-1
        if k < self.k_limit:
            base_values.append((1 << (k+1)) - 1)  # 2^(k+1)-1
        if k < self.k_limit - 1:
            base_values.append((1 << (k+2)) - 1)  # 2^(k+2)-1
        
        # 策略2：添加常见错误值（如混淆k值或直接使用2^k）
        common_errors = [k, (1 << k), correct_value * 2, correct_value // 2 if correct_value > 1 else 0]
        all_candidates = list(set(base_values + common_errors))  # 去重
        all_candidates = [c for c in all_candidates if c != correct_value and c >= 0]  # 排除正确答案和负数
        
        # 选择3个最合适的干扰项
        while len(distractors) < 3 and all_candidates:
            candidate = random.choice(all_candidates)
            distractors.add(candidate)
            all_candidates.remove(candidate)
        
        # 如果候选不足，补充随机数
        while len(distractors) < 3:
            fake = correct_value + random.randint(-5, 5) * 2
            if fake != correct_value and fake > 0:
                distractors.add(fake)
        
        return list(distractors)[:3]
    
    def generate_choice_question(self, show_explanation=True):
        """
        生成一道选择题。
        题型随机：1.计算退避窗口；2.计算最大退避时间；3.判断是否需要重传。
        """
        collision_count, frame_id = self.generate_params()
        effective_k = min(collision_count, self.k_limit)
        window = self._calculate_backoff_window(collision_count)
        
        # 随机选择一种问题类型
        question_type = random.choice(['window', 'max_time', 'retransmit'])
        
        if question_type == 'window':
            # 题型1：计算退避窗口大小
            question = f"在CSMA/CD协议中，{frame_id}发送时发生第{collision_count}次冲突，则其退避窗口的大小为（ ）"
            correct = window
            unit = ""
            explanation = f"根据二进制指数退避算法，退避窗口大小 W = 2^k - 1，其中 k = min(冲突次数, 10)。第{collision_count}次冲突时 k={effective_k}，故 W=2^{effective_k} - 1 = {window}。"
        
        elif question_type == 'max_time':
            # 题型2：计算最大退避时间
            max_time_ms = window * self.slot_time / 1000  # 转换为毫秒，符合真题格式[citation:4]
            question = f"已知10BaseT以太网的争用期为{self.slot_time}μs，若{frame_id}发送时发生第{collision_count}次冲突，则最大退避时间为（ ）"
            correct = round(max_time_ms, 4)  # 保留4位小数，匹配真题精度
            unit = "ms"
            explanation = f"第{collision_count}次冲突时 k={effective_k}，退避窗口 W=2^{effective_k} - 1 = {window}。最大退避时间 = {window} × {self.slot_time}μs = {correct}ms。"
        
        else:
            # 题型3：判断是否需要重传（超过16次则丢弃）
            question = f"在CSMA/CD协议中，{frame_id}发送时已发生{collision_count}次冲突，则接下来应（ ）"
            options_text = ["A. 立即重传", "B. 从退避窗口选择随机时间后重传", "C. 丢弃该帧，报告错误", "D. 等待固定时间后重传"]
            if collision_count < self.max_collisions:
                correct_text = "B. 从退避窗口选择随机时间后重传"
                explanation = f"二进制指数退避算法规定，冲突次数小于{self.max_collisions}次时，站点从[0, 2^k-1]中随机选择退避时间后重传。本题冲突次数为{collision_count}，小于{self.max_collisions}，故需退避后重传。"
            else:
                correct_text = "C. 丢弃该帧，报告错误"
                explanation = f"算法规定最大重传次数为{self.max_collisions}次，超过此次数则丢弃帧。本题冲突次数为{collision_count}，已达到上限，故应丢弃。"
            
            # 对于文本型选择题，直接返回特定格式
            if show_explanation:
                return question, options_text, correct_text, explanation
            else:
                return question, options_text, correct_text, ""
        
        # 生成数值型选择题的选项
        distractors = self._generate_distractors(correct, effective_k)
        all_options = distractors + [correct]
        random.shuffle(all_options)
        
        # 构建选项文本 (A. xxx B. xxx ...)
        options_text = [f"{chr(65+i)}. {opt}{unit}" for i, opt in enumerate(all_options)]
        correct_letter = chr(65 + all_options.index(correct))
        correct_text = f"{correct_letter}. {correct}{unit}"
        
        if not show_explanation:
            explanation = ""
        
        return question, options_text, correct_text, explanation
    
    def generate_fill_question(self, show_explanation=True):
        """
        生成一道填空题。
        题型随机：1.填写取值范围；2.计算最大/具体退避时间[citation:4]。
        """
        collision_count, frame_id = self.generate_params()
        effective_k = min(collision_count, self.k_limit)
        window = self._calculate_backoff_window(collision_count)
        
        question_type = random.choice(['range', 'time_calc'])
        
        if question_type == 'range':
            # 题型1：填写取值范围
            question = f"在CSMA/CD协议中，若{frame_id}第{collision_count}次冲突后选择退避时间，其可选退避时间的取值范围是______（单位：争用期）。"
            answer = f"[0, 1, 2, ..., {window}]"
            explanation = f"第{collision_count}次冲突时 k={effective_k}，退避窗口 W=2^{effective_k} - 1 = {window}，因此可从0到{window}之间随机选择一个整数作为退避的争用期数量。"
        
        else:
            # 题型2：计算具体时间（最大或随机一个）
            if random.choice([True, False]):
                # 计算最大退避时间
                time_value = window * self.slot_time
                question = f"已知争用期为{self.slot_time}μs，若{frame_id}第{collision_count}次冲突后选择退避，则最大退避时间为______μs。"
                answer = f"{round(time_value, 1)}"  # 保留1位小数
                explanation = f"第{collision_count}次冲突时 k={effective_k}，最大退避争用期数 = 2^{effective_k} - 1 = {window}，最大退避时间 = {window} × {self.slot_time}μs = {answer}μs。"
            else:
                # 计算一个随机选择的退避时间
                random_slot = random.randint(0, window)
                time_value = random_slot * self.slot_time
                question = f"已知争用期为{self.slot_time}μs，若{frame_id}第{collision_count}次冲突后随机选择退避{random_slot}个争用期，则退避时间为______μs。"
                answer = f"{round(time_value, 1)}"
                explanation = f"退避时间 = 随机选择的争用期数 × 争用期时长 = {random_slot} × {self.slot_time}μs = {answer}μs。"
        
        if not show_explanation:
            explanation = ""
        
        return question, answer, explanation
    
    def generate_questions_batch(self, num_questions=5, question_type='choice', show_explanation=True):
        """
        批量生成题目，输出为Markdown格式。
        :param num_questions: 题目数量
        :param question_type: 'choice' 或 'fill'
        :param show_explanation: 是否显示解析
        """
        output_lines = []
        output_lines.append(f"## 生成的二进制指数退避算法题目 ({question_type}, 共{num_questions}题)\n")
        
        for i in range(num_questions):
            output_lines.append(f"### 第{i+1}题")
            
            if question_type == 'choice':
                q, options, correct, expl = self.generate_choice_question(show_explanation)
                output_lines.append(q)
                output_lines.append("")  # 空行
                for opt in options:
                    output_lines.append(f"- {opt}")
                output_lines.append("")
                output_lines.append(f"**正确答案：** {correct}")
                
            else:  # fill
                q, answer, expl = self.generate_fill_question(show_explanation)
                output_lines.append(q)
                output_lines.append("")
                output_lines.append(f"**正确答案：** {answer}")
            
            if show_explanation:
                output_lines.append("")
                output_lines.append(f"**解析：** {expl}")
            
            output_lines.append("")  # 题目间隔空行
        
        return "\n".join(output_lines)


def main():
    """主函数：提供命令行交互和参数解析。"""
    parser = argparse.ArgumentParser(description="二进制指数退避算法考题生成器 (408考点)")
    parser.add_argument("--num", type=int, default=1, help="生成题目数量 (默认: 1)")
    parser.add_argument("--type", choices=["choice", "fill", "both"], default="both", help="题目类型: choice(选择), fill(填空), both(随机混合) (默认: both)")
    parser.add_argument("--no-explanation", action="store_true", help="不显示解析")
    parser.add_argument("--batch", action="store_true", help="批量模式，直接输出Markdown")
    
    args = parser.parse_args()
    
    generator = BackoffQuestionGenerator()
    
    if args.batch:
        # 批量生成模式，直接输出
        q_type = args.type if args.type != "both" else random.choice(["choice", "fill"])
        print(generator.generate_questions_batch(args.num, q_type, not args.no_explanation))
        return
    
    # 交互式模式
    print("=== 二进制指数退避算法考题生成器 (适配408考点) ===")
    print("参考真题：2023年第36题[citation:6]、2025年第35题[citation:4]等")
    
    while True:
        print("\n" + "="*50)
        print("请选择操作:")
        print("  1. 生成选择题")
        print("  2. 生成填空题")
        print("  3. 批量生成题目 (Markdown格式)")
        print("  4. 退出")
        
        choice = input("请输入选项 (1-4): ").strip()
        
        if choice == "1":
            q, opts, correct, expl = generator.generate_choice_question(not args.no_explanation)
            print("\n" + "="*30)
            print("题目:", q)
            print("\n选项:")
            for opt in opts:
                print(" ", opt)
            print("\n正确答案:", correct)
            if expl:
                print("解析:", expl)
        
        elif choice == "2":
            q, answer, expl = generator.generate_fill_question(not args.no_explanation)
            print("\n" + "="*30)
            print("题目:", q)
            print("\n正确答案:", answer)
            if expl:
                print("解析:", expl)
        
        elif choice == "3":
            num = int(input("请输入要生成的题目数量: "))
            q_type = input("请输入题目类型 (choice/fill/both): ").lower()
            if q_type not in ["choice", "fill", "both"]:
                q_type = "both"
            
            if q_type == "both":
                q_type = random.choice(["choice", "fill"])
            
            print("\n" + "="*50)
            print(generator.generate_questions_batch(num, q_type, not args.no_explanation))
            print("\n提示：以上内容可直接复制到Markdown文档中。")
        
        elif choice == "4":
            print("程序退出。")
            break
        
        else:
            print("无效输入，请重新选择。")

if __name__ == "__main__":
    main()