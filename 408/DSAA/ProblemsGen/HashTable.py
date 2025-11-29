import math
import random


class HashTableQuestionGenerator:
    def __init__(self):
        self.question_types = [
            "load_factor",
            "conflict_sequence",
            "search_failure_probes",
            "hash_function_analysis"
        ]

    def generate_question(self, q_type: str = None):
        """生成指定类型的题目"""
        if q_type is None:
            q_type = random.choice(self.question_types)

        if q_type == "load_factor":
            return self._generate_load_factor_question()
        elif q_type == "conflict_sequence":
            return self._generate_conflict_sequence_question()
        elif q_type == "search_failure_probes":
            return self._generate_search_failure_question()
        elif q_type == "hash_function_analysis":
            return self._generate_hash_function_question()
        else:
            raise ValueError(f"未知的题目类型: {q_type}")

    @staticmethod
    def _generate_load_factor_question():
        """生成负载因子相关题目"""
        m = random.choice([11, 13, 17, 19, 23, 29, 31])  # 哈希表大小（质数）
        n = random.randint(m // 3, m - 2)  # 元素数量

        question = f"设哈希表长度为 m={m}，已存储 n={n} 个元素，求：\n"
        question += "(1) 当前负载因子 α\n"
        question += "(2) 如果再插入 k=3 个元素，负载因子变为多少？\n"
        question += "(3) 要使负载因子不超过 0.75，最多还能插入多少个元素？"

        answer = f"(1) 当前负载因子 α = n/m = {n}/{m} = {n / m:.3f}\n"
        answer += f"(2) 插入3个元素后，α' = (n+3)/m = {n + 3}/{m} = {(n + 3) / m:.3f}\n"

        max_additional = int(m * 0.75) - n
        answer += f"(3) 负载因子上限 0.75，对应最大元素数: 0.75×{m} = {int(m * 0.75)}\n"
        answer += f"    还能插入元素数: {int(m * 0.75)} - {n} = {max_additional}"

        explanation = "负载因子 α = 表中元素数 / 哈希表长度，反映了哈希表的装满程度。"

        return {
            "question": question,
            "answer": answer,
            "explanation": explanation,
            "type": "load_factor"
        }

    @staticmethod
    def _generate_conflict_sequence_question():
        """生成冲突探测序列题目"""
        m = random.choice([11, 13, 17, 19])
        keys = [random.randint(10, 99) for _ in range(3)]
        hash_func = f"h(key) = key % {m}"

        probe_methods = ["线性探测", "平方探测", "双散列"]
        method = random.choice(probe_methods)

        question = f"哈希表长度 m={m}，哈希函数 {hash_func}\n"
        question += f"关键字序列: {keys}\n"
        question += f"使用{method}法处理冲突，请计算：\n"

        if method == "线性探测":
            question += "(1) 每个关键字的探测序列（列出前5次探测位置）\n"
            question += "(2) 成功查找到所有关键字所需的平均探测次数"

            answer = "(1) 探测序列：\n"
            total_probes = 0
            for key in keys:
                h0 = key % m
                sequence = [h0]
                for i in range(1, 5):
                    sequence.append((h0 + i) % m)
                answer += f"    key={key}: {sequence}\n"
                total_probes += sequence.index(h0) + 1

            avg_probes = total_probes / len(keys)
            answer += f"(2) 平均探测次数: {avg_probes:.2f}"

            explanation = "线性探测法：h_i(key) = (h(key) + i) % m，依次检查后续位置"

        elif method == "平方探测":
            question += "(1) 每个关键字的探测序列（列出前5次探测位置）\n"
            question += "(2) 说明平方探测法可能遇到的问题"

            answer = "(1) 探测序列：\n"
            for key in keys:
                h0 = key % m
                sequence = [h0]
                for i in range(1, 5):
                    probe_pos = (h0 + (-1 if i % 2 == 0 else 1) * ((i + 1) // 2) ** 2) % m
                    sequence.append(probe_pos)
                answer += f"    key={key}: {sequence}\n"

            answer += "(2) 平方探测法可能无法探测到所有位置，当 m=4k+3 形式的质数时效果最好"

            explanation = "平方探测法：h_i(key) = (h(key) ± i²) % m，交替使用正负平方项"

        else:  # 双散列
            h2_func = f"h2(key) = 1 + (key % {m - 1})"
            question += f"(1) 使用第二散列函数 {h2_func}，计算探测序列\n"
            question += "(2) 解释为什么第二散列函数要满足什么条件"

            answer = "(1) 探测序列：\n"
            for key in keys:
                h1 = key % m
                h2 = 1 + (key % (m - 1))
                sequence = [h1]
                for i in range(1, 5):
                    sequence.append((h1 + i * h2) % m)
                answer += f"    key={key}: h1={h1}, h2={h2}, 序列: {sequence}\n"

            answer += f"(2) 第二散列函数 h2(key) 必须与表长 {m} 互质，且 h2≠0"

            explanation = "双散列法：h_i(key) = (h1(key) + i×h2(key)) % m，使用两个不同的散列函数"

        return {
            "question": question,
            "answer": answer,
            "explanation": explanation,
            "type": "conflict_sequence"
        }

    @staticmethod
    def _generate_search_failure_question():
        """生成查找失败探测次数题目"""
        m = random.choice([7, 11, 13, 17])
        n = random.randint(m // 2, m - 3)
        alpha = n / m

        question = f"哈希表长度 m={m}，已有 n={n} 个元素，负载因子 α={alpha:.2f}\n"
        question += "使用开放定址法处理冲突，计算查找失败时需要的平均探测次数：\n"

        methods = [
            ("线性探测", "1/2 × (1 + 1/(1-α)²)"),
            ("平方探测", "-1/α × ln(1-α)"),
            ("双散列", "1/(1-α)")
        ]

        method_name, formula = random.choice(methods)
        question += f"采用{method_name}法"

        # 计算理论值
        if method_name == "线性探测":
            theoretical = 0.5 * (1 + 1 / ((1 - alpha) ** 2))
        elif method_name == "平方探测":
            theoretical = -math.log(1 - alpha) / alpha if alpha > 0 else 1
        else:  # 双散列
            theoretical = 1 / (1 - alpha) if alpha < 1 else float('inf')

        answer = f"{method_name}法查找失败的平均探测次数公式: {formula}\n"
        answer += f"代入 α={alpha:.3f}:\n"
        answer += f"计算结果 = {theoretical:.3f}"

        explanation = f"查找失败时，需要一直探测直到遇到空位置。{method_name}法的探测序列特性决定了平均探测次数。"

        return {
            "question": question,
            "answer": answer,
            "explanation": explanation,
            "type": "search_failure_probes"
        }

    @staticmethod
    def _generate_hash_function_question():
        """生成散列函数分析题目"""
        m = random.choice([16, 32, 64, 128])
        hash_functions = [
            f"h(key) = key % {m}",
            f"h(key) = key × ({m}-1) % {m}",
            f"h(key) = ⌊{m} × (key × 0.618)⌋ % {m}",
            f"h(key) = (key + key//{m}) % {m}"
        ]

        func = random.choice(hash_functions)

        question = f"分析散列函数 {func} 的特性：\n"
        question += "(1) 该函数是否满足均匀性要求？为什么？\n"
        question += "(2) 如果关键字分布不均匀，会产生什么影响？\n"
        question += "(3) 提出改进建议（如需要）"

        if "key %" in func:
            answer = "(1) 满足均匀性要求。取模运算能将关键字均匀分布\n"
            answer += "(2) 如果关键字本身分布不均匀，取模后仍能较好分散\n"
            answer += "(3) 这是一个较好的散列函数，无需特别改进"
            explanation = "简单的取模运算在大多数情况下都能提供良好的分布特性"
        elif "0.618" in func:
            answer = "(1) 满足均匀性要求。使用黄金分割比能提供良好的分布\n"
            answer += "(2) 对关键字的分布不敏感，适应性较好\n"
            answer += "(3) 乘法运算可能稍慢，但分布特性优秀"
            explanation = "乘法散列法利用无理数的特性提供良好的随机分布"
        else:
            answer = "(1) 可能需要验证，某些运算可能导致分布不均匀\n"
            answer += "(2) 如果运算设计不当，可能加剧冲突\n"
            answer += "(3) 建议使用更简单的取模运算或验证分布均匀性"
            explanation = "散列函数设计需要考虑分布均匀性和计算效率的平衡"

        return {
            "question": question,
            "answer": answer,
            "explanation": explanation,
            "type": "hash_function_analysis"
        }


def main():
    generator = HashTableQuestionGenerator()

    print("哈希表计算题目生成器")
    print("=" * 50)

    # 生成各种类型的题目
    for i in range(3):
        print(f"\n题目 {i + 1}:")
        question_data = generator.generate_question()

        print("【题目】")
        print(question_data["question"])

        print("\n【答案】")
        print(question_data["answer"])

        print("\n【解析】")
        print(question_data["explanation"])

        print("\n" + "-" * 50)


if __name__ == "__main__":
    main()
