import random


class MatrixOperationGenerator:
    def __init__(self):
        self.matrix_sizes = [(2, 2), (2, 3), (3, 2), (3, 3)]

    @staticmethod
    def generate_matrix(rows, cols, min_val=-5, max_val=5):
        """生成指定大小的矩阵"""
        return [[random.randint(min_val, max_val) for _ in range(cols)] for _ in range(rows)]

    @staticmethod
    def matrix_to_string(matrix):
        """将矩阵转换为字符串表示"""
        rows = []
        for row in matrix:
            row_str = "  [" + "  ".join(f"{x:3}" for x in row) + "]"
            rows.append(row_str)
        return "\n".join(rows)

    @staticmethod
    def matrix_addition(a, b):
        """矩阵加法"""
        rows, cols = len(a), len(a[0])
        return [[a[i][j] + b[i][j] for j in range(cols)] for i in range(rows)]

    @staticmethod
    def matrix_subtraction(a, b):
        """矩阵减法"""
        rows, cols = len(a), len(a[0])
        return [[a[i][j] - b[i][j] for j in range(cols)] for i in range(rows)]

    @staticmethod
    def scalar_multiplication(k, a):
        """数乘矩阵"""
        return [[k * a[i][j] for j in range(len(a[0]))] for i in range(len(a))]

    @staticmethod
    def matrix_multiplication(a, b):
        """矩阵乘法"""
        rows_a, cols_a = len(a), len(a[0])
        rows_b, cols_b = len(b), len(b[0])

        result = [[0 for _ in range(cols_b)] for _ in range(rows_a)]

        for i in range(rows_a):
            for j in range(cols_b):
                for k in range(cols_a):
                    result[i][j] += a[i][k] * b[k][j]

        return result

    @staticmethod
    def matrix_transpose(a):
        """矩阵转置"""
        rows, cols = len(a), len(a[0])
        return [[a[j][i] for j in range(rows)] for i in range(cols)]

    def generate_question_type_1(self):
        """生成矩阵基本运算题目：加减、数乘"""
        rows, cols = random.choice(self.matrix_sizes)
        a = self.generate_matrix(rows, cols)
        b = self.generate_matrix(rows, cols)
        k = random.randint(2, 5)

        question = f"已知矩阵：\na = \n{self.matrix_to_string(a)}\n\nb = \n{self.matrix_to_string(b)}\n\n常数 k = {k}\n\n"
        question += "计算：\n1. a + b\n2. a - b\n3. kA\n4. kB"

        return question, a, b, k

    def generate_question_type_2(self):
        """生成矩阵乘法题目"""
        # 确保矩阵乘法可行
        size_pairs = [((2, 2), (2, 2)), ((2, 3), (3, 2)), ((3, 2), (2, 3)), ((3, 3), (3, 3))]
        (rows_a, cols_a), (rows_b, cols_b) = random.choice(size_pairs)

        a = self.generate_matrix(rows_a, cols_a)
        b = self.generate_matrix(rows_b, cols_b)

        question = f"已知矩阵：\na = \n{self.matrix_to_string(a)}\n\nb = \n{self.matrix_to_string(b)}\n\n"
        question += "计算：\n1. a × b\n2. b × a（如果可乘）"

        return question, a, b

    def generate_question_type_3(self):
        """生成转置运算题目"""
        rows, cols = random.choice(self.matrix_sizes)
        a = self.generate_matrix(rows, cols)
        b = self.generate_matrix(rows, cols)

        question = f"已知矩阵：\na = \n{self.matrix_to_string(a)}\n\nb = \n{self.matrix_to_string(b)}\n\n"
        question += "计算：\n1. Aᵀ\n2. Bᵀ\n3. (a + b)ᵀ\n4. Aᵀ + Bᵀ\n5. 验证转置的分配律：(a + b)ᵀ = Aᵀ + Bᵀ"

        return question, a, b

    def generate_answer_and_explanation(self, question_type, *args):
        """生成答案和解析"""
        if question_type == 1:
            return self._answer_type_1(*args)
        elif question_type == 2:
            return self._answer_type_2(*args)
        elif question_type == 3:
            return self._answer_type_3(*args)

    def _answer_type_1(self, a, b, k):
        """类型1题目的答案和解析"""
        answer = "【答案】\n"
        explanation = "【解析】\n"

        # 1. a + b
        a_plus_b = self.matrix_addition(a, b)
        answer += f"1. a + b = \n{self.matrix_to_string(a_plus_b)}\n\n"
        explanation += "1. 矩阵加法：对应元素相加\n"
        explanation += f"   例如：a[0][0] + b[0][0] = {a[0][0]} + {b[0][0]} = {a_plus_b[0][0]}\n\n"

        # 2. a - b
        a_minus_b = self.matrix_subtraction(a, b)
        answer += f"2. a - b = \n{self.matrix_to_string(a_minus_b)}\n\n"
        explanation += "2. 矩阵减法：对应元素相减\n"
        explanation += f"   例如：a[0][0] - b[0][0] = {a[0][0]} - {b[0][0]} = {a_minus_b[0][0]}\n\n"

        # 3. kA
        k_a = self.scalar_multiplication(k, a)
        answer += f"3. kA = \n{self.matrix_to_string(k_a)}\n\n"
        explanation += f"3. 数乘矩阵：每个元素乘以常数k={k}\n"
        explanation += f"   例如：k × a[0][0] = {k} × {a[0][0]} = {k_a[0][0]}\n\n"

        # 4. kB
        k_b = self.scalar_multiplication(k, b)
        answer += f"4. kB = \n{self.matrix_to_string(k_b)}\n\n"
        explanation += f"4. 数乘矩阵：每个元素乘以常数k={k}\n"
        explanation += f"   例如：k × b[0][0] = {k} × {b[0][0]} = {k_b[0][0]}\n"

        return answer, explanation

    def _answer_type_2(self, a, b):
        """类型2题目的答案和解析"""
        answer = "【答案】\n"
        explanation = "【解析】\n"

        # 1. a × b
        if len(a[0]) == len(b):
            a_b = self.matrix_multiplication(a, b)
            answer += f"1. a × b = \n{self.matrix_to_string(a_b)}\n\n"
            explanation += "1. 矩阵乘法：A的行乘以B的列求和\n"
            explanation += f"   例如：AB[0][0] = A的第0行与B的第0列对应元素乘积之和\n"
            explanation += \
                f"         = {' + '.join(f'{a[0][k]}×{b[k][0]}' for k in range(len(a[0])))} = {a_b[0][0]}\n\n"
        else:
            answer += "1. a × b 不可乘（A的列数不等于B的行数）\n\n"
            explanation += "1. a × b 不可乘：A的列数 ≠ B的行数\n\n"

        # 2. b × a
        if len(b[0]) == len(a):
            b_a = self.matrix_multiplication(b, a)
            answer += f"2. b × a = \n{self.matrix_to_string(b_a)}\n\n"
            explanation += "2. 矩阵乘法：B的行乘以A的列求和\n"
            explanation += f"   例如：BA[0][0] = B的第0行与A的第0列对应元素乘积之和\n"
            explanation += f"         = {' + '.join(f'{b[0][k]}×{a[k][0]}' for k in range(len(b[0])))} = {b_a[0][0]}\n"
        else:
            answer += "2. b × a 不可乘（B的列数不等于A的行数）\n\n"
            explanation += "2. b × a 不可乘：B的列数 ≠ A的行数\n"

        return answer, explanation

    def _answer_type_3(self, a, b):
        """类型3题目的答案和解析"""
        answer = "【答案】\n"
        explanation = "【解析】\n"

        # 1. Aᵀ
        a_t = self.matrix_transpose(a)
        answer += f"1. Aᵀ = \n{self.matrix_to_string(a_t)}\n\n"
        explanation += "1. 矩阵转置：行变列，列变行\n"
        explanation += f"   例如：原A[{0}][{1}] = {a[0][1]} 变为 Aᵀ[{1}][{0}] = {a_t[1][0]}\n\n"

        # 2. Bᵀ
        b_t = self.matrix_transpose(b)
        answer += f"2. Bᵀ = \n{self.matrix_to_string(b_t)}\n\n"
        explanation += "2. 矩阵转置：行变列，列变行\n\n"

        # 3. (a + b)ᵀ
        a_plus_b = self.matrix_addition(a, b)
        a_plus_b_t = self.matrix_transpose(a_plus_b)
        answer += f"3. (a + b)ᵀ = \n{self.matrix_to_string(a_plus_b_t)}\n\n"
        explanation += "3. 先计算 a + b，再转置\n"
        explanation += f"   a + b = \n{self.matrix_to_string(a_plus_b)}\n"
        explanation += f"   然后转置得到上述结果\n\n"

        # 4. Aᵀ + Bᵀ
        a_t_plus_b_t = self.matrix_addition(a_t, b_t)
        answer += f"4. Aᵀ + Bᵀ = \n{self.matrix_to_string(a_t_plus_b_t)}\n\n"
        explanation += "4. 先分别转置 a 和 b，再相加\n\n"

        # 5. 验证
        answer += "5. 验证："
        if a_plus_b_t == a_t_plus_b_t:
            answer += "(a + b)ᵀ = Aᵀ + Bᵀ 成立 ✓\n"
            explanation += "5. 验证转置分配律：\n"
            explanation += "   (a + b)ᵀ 和 Aᵀ + Bᵀ 的结果相同\n"
            explanation += "   因此 (a + b)ᵀ = Aᵀ + Bᵀ 成立\n"
            explanation += "   这验证了转置运算的分配律"
        else:
            answer += "(a + b)ᵀ ≠ Aᵀ + Bᵀ 不成立\n"
            explanation += "5. 验证转置分配律：结果不相同，但理论上应该成立，请检查计算过程\n"

        return answer, explanation


def main():
    generator = MatrixOperationGenerator()

    print("矩阵基本运算题目生成器")
    print("=" * 50)

    # 生成三种类型的题目
    for i in range(3):
        print(f"\n题目 {i + 1}:")
        print("-" * 30)

        if i == 0:
            # 类型1：加减、数乘
            question, a, b, k = generator.generate_question_type_1()  # 现在返回所有需要的数据
            print(question)
            print("\n" + "=" * 50)

            # 显示答案
            answer, explanation = generator.generate_answer_and_explanation(1, a, b, k)
            print(answer)
            print(explanation)

        elif i == 1:
            # 类型2：乘法
            question, a, b = generator.generate_question_type_2()
            print(question)
            print("\n" + "=" * 50)

            # 显示答案
            answer, explanation = generator.generate_answer_and_explanation(2, a, b)
            print(answer)
            print(explanation)

        else:
            # 类型3：转置
            question, a, b = generator.generate_question_type_3()
            print(question)
            print("\n" + "=" * 50)

            # 显示答案
            answer, explanation = generator.generate_answer_and_explanation(3, a, b)
            print(answer)
            print(explanation)


if __name__ == "__main__":
    main()
