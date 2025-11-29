import random
from typing import List, Tuple, Dict


class HuffmanWPLGenerator:
    def __init__(self):
        self.rules = {
            "核心规则": [
                "哈夫曼树是带权路径长度(WPL)最小的二叉树",
                "WPL = Σ(权值 × 路径长度)，其中路径长度是从根节点到该节点的边数",
                "构建方法：每次选择两个最小的权值合并，新节点权值为两者之和",
                "WPL等于所有非叶子节点权值之和（构建过程中合并产生的新节点权值之和）"
            ],
            "高频场景复杂度": [
                "n个权值构建哈夫曼树的时间复杂度：O(n log n)",
                "空间复杂度：O(n)",
                "最优性：哈夫曼编码是最优前缀码"
            ]
        }

    @staticmethod
    def generate_weights(n: int, min_val: int = 1, max_val: int = 20) -> List[int]:
        """生成一组权值"""
        return sorted([random.randint(min_val, max_val) for _ in range(n)])

    @staticmethod
    def calculate_wpl(weights: List[int]) -> Tuple[int, List[Tuple]]:
        """计算WPL并返回构建过程"""
        wpl = 0
        process = []
        current_weights = weights.copy()

        while len(current_weights) > 1:
            # 排序并选择最小的两个
            current_weights.sort()
            a, b = current_weights[0], current_weights[1]
            new_weight = a + b
            wpl += new_weight

            process.append((a, b, new_weight, current_weights.copy()))

            # 更新权值列表
            current_weights = current_weights[2:] + [new_weight]

        return wpl, process

    def generate_basic_question(self) -> Dict:
        """生成基础计算题"""
        n = random.randint(4, 7)
        weights = self.generate_weights(n)
        wpl, process = self.calculate_wpl(weights)

        question = f"给定权值集合 {weights}，构建哈夫曼树，计算带权路径长度(WPL)。"

        solution = f"解：\n"
        solution += f"1. 初始权值集合: {weights}\n"
        solution += f"2. 构建过程：\n"

        for i, (a, b, new, state) in enumerate(process, 1):
            solution += f"   步骤{i}: 合并 {a} 和 {b}，得到新节点 {new}，当前WPL累计: {sum([step[2] for step in process[:i]])}\n"

        solution += f"3. 最终WPL = {wpl}\n"
        solution += f"4. 验证：WPL等于所有非叶子节点权值之和 = {' + '.join([str(step[2]) for step in process])} = {wpl}"

        return {
            "type": "基础计算",
            "question": question,
            "solution": solution,
            "weights": weights,
            "wpl": wpl,
            "difficulty": "简单"
        }

    def generate_algebra_question(self) -> Dict:
        """生成代数推演题"""
        # 生成代数表达式相关的权值
        base_weights = self.generate_weights(3, 2, 10)
        x_val = random.randint(2, 5)

        weights = [f"{w}x" for w in base_weights]
        numeric_weights = [w * x_val for w in base_weights]
        wpl, _ = self.calculate_wpl(numeric_weights)

        question = f"给定权值集合 {weights}，其中x={x_val}，构建哈夫曼树，用代数式表示WPL。"

        # 计算代数形式的WPL
        sorted_base = sorted(base_weights)
        algebraic_wpl = f"{sorted_base[0] + sorted_base[1]}x + {sorted_base[0] + sorted_base[1] + sorted_base[2]}x"

        solution = f"解：\n"
        solution += f"1. 数值权值: {numeric_weights}\n"
        solution += f"2. 排序后: {sorted(numeric_weights)}\n"
        solution += f"3. 代数构建过程：\n"
        solution += f"   - 首先合并 {sorted_base[0]}x 和 {sorted_base[1]}x，得到 {(sorted_base[0] + sorted_base[1])}x\n"
        solution += f"   - 然后合并 {(sorted_base[0] + sorted_base[1])}x 和 {sorted_base[2]}x，" \
                    f"得到 {(sorted_base[0] + sorted_base[1] + sorted_base[2])}x\n"
        solution += f"4. WPL代数式 = {algebraic_wpl} = {wpl}"

        return {
            "type": "代数推演",
            "question": question,
            "solution": solution,
            "weights": weights,
            "algebraic_wpl": algebraic_wpl,
            "numeric_wpl": wpl,
            "difficulty": "中等"
        }

    @staticmethod
    def generate_complexity_question() -> Dict:
        """生成复杂度分析题"""
        n = random.choice([8, 16, 32, 64])

        question = f"对于{n}个权值构建哈夫曼树：\n"
        question += "(1) 分析构建过程的时间复杂度\n"
        question += "(2) 如果权值已经排序，如何优化构建过程\n"
        question += "(3) WPL计算的时间复杂度是多少"

        solution = f"解：\n"
        solution += f"(1) 时间复杂度分析：\n"
        solution += f"    - 每次需要选择两个最小权值：O(n)时间\n"
        solution += f"    - 需要进行n-1次合并：O(n)次\n"
        solution += f"    - 使用数组存储：总时间复杂度 O(n²)\n"
        solution += f"    - 使用优先队列(堆)：总时间复杂度 O(n log n)\n\n"

        solution += f"(2) 权值已排序的优化：\n"
        solution += f"    - 维护两个队列：原始权值队列(已排序)和新节点队列\n"
        solution += f"    - 每次从两个队列头部选择较小的两个权值\n"
        solution += f"    - 时间复杂度可优化到 O(n)\n\n"

        solution += f"(3) WPL计算复杂度：\n"
        solution += f"    - 在构建过程中累计计算：O(1)额外时间\n"
        solution += f"    - 总体与构建过程同阶：O(n log n)"

        return {
            "type": "复杂度分析",
            "question": question,
            "solution": solution,
            "n": n,
            "difficulty": "困难"
        }

    @staticmethod
    def generate_proof_question() -> Dict:
        """生成证明题"""
        questions = [
            {
                "question": "证明：哈夫曼树的WPL等于所有非叶子节点权值之和",
                "hint": "考虑每个叶子节点的路径长度与其在合并过程中被计算的次数之间的关系"
            },
            {
                "question": "证明：哈夫曼编码是最优前缀码",
                "hint": "使用反证法，假设存在更优编码，推导矛盾"
            }
        ]

        selected = random.choice(questions)

        solution = f"证明思路：\n"
        solution += f"{selected['hint']}\n\n"
        solution += f"详细证明：\n"

        if "非叶子节点" in selected['question']:
            solution += f"1. 设叶子节点权值为w_i，路径长度为l_i\n"
            solution += f"2. WPL = Σ(w_i × l_i)\n"
            solution += f"3. 每个叶子节点在合并过程中，其权值会被累加l_i次\n"
            solution += f"4. 因此WPL等于所有合并产生的新节点权值之和\n"
            solution += f"5. 这些新节点就是所有的非叶子节点"
        else:
            solution += f"1. 假设存在比哈夫曼编码更优的前缀码\n"
            solution += f"2. 则该编码对应的二叉树WPL更小\n"
            solution += f"3. 但哈夫曼树的WPL已经是最小的\n"
            solution += f"4. 矛盾，因此哈夫曼编码是最优的"

        return {
            "type": "数学证明",
            "question": selected['question'],
            "solution": solution,
            "difficulty": "困难"
        }

    def generate_question_set(self, count: int = 4) -> List[Dict]:
        """生成一套题目"""
        generators = [
            self.generate_basic_question,
            self.generate_algebra_question,
            self.generate_complexity_question,
            self.generate_proof_question
        ]

        questions = []
        for i in range(min(count, len(generators))):
            questions.append(generators[i]())

        return questions

    def display_rules(self):
        """显示核心规则"""
        print("=== 哈夫曼树WPL计算核心规则 ===")
        for category, rules in self.rules.items():
            print(f"\n{category}:")
            for i, rule in enumerate(rules, 1):
                print(f"  {i}. {rule}")


# 使用示例
def main():
    generator = HuffmanWPLGenerator()

    print("哈夫曼树WPL计算题目生成器")
    print("=" * 50)

    # 显示核心规则
    generator.display_rules()

    print("\n" + "=" * 50)
    print("生成的题目集：")
    print("=" * 50)

    # 生成题目
    questions = generator.generate_question_set(4)

    for i, q in enumerate(questions, 1):
        print(f"\n题目{i} [{q['type']}] - 难度: {q['difficulty']}")
        print(f"问题: {q['question']}")
        print("-" * 40)

        if 'weights' in q:
            print(f"权值: {q['weights']}")
        if 'wpl' in q:
            print(f"WPL: {q['wpl']}")

        input("\n按回车查看答案...")
        print(f"\n答案:")
        print(q['solution'])
        print("=" * 50)


if __name__ == "__main__":
    main()
