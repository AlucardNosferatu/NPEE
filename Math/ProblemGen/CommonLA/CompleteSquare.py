import random

import sympy as sp
from sympy import symbols


# noinspection PyPep8Naming
class QuadraticFormGenerator:
    def __init__(self, num_vars=3):
        self.num_vars = num_vars
        self.vars = symbols(f'x1:{num_vars + 1}')

    def generate_regular_problem(self):
        """生成常规题（需要配方）"""
        # 生成随机对称系数矩阵
        A = sp.zeros(self.num_vars)
        for i in range(self.num_vars):
            for j in range(i, self.num_vars):
                if i == j:
                    A[i, j] = random.randint(1, 3)
                else:
                    coeff = random.randint(1, 2)
                    A[i, j] = coeff
                    A[j, i] = coeff

        # 构造二次多项式
        poly = 0
        for i in range(self.num_vars):
            for j in range(self.num_vars):
                if i == j:
                    poly += A[i, j] * self.vars[i] ** 2
                else:
                    poly += A[i, j] * self.vars[i] * self.vars[j]

        return poly, "常规题", None

    def generate_trap_problem(self):
        """生成陷阱题（已配好但变换不可逆，且配方个数等于未知数个数）"""
        # 构造一个行列式为0但满行的变换矩阵
        # 方法：创建一个矩阵，其中某两行线性相关
        while True:
            T = sp.zeros(self.num_vars)

            # 生成前n-1行，确保它们线性无关
            for i in range(self.num_vars - 1):
                for j in range(self.num_vars):
                    T[i, j] = random.randint(-2, 2)

            # 最后一行是前两行的线性组合，确保行列式为0
            # 但系数选择要确保最后一行不是零向量
            alpha = random.randint(1, 2)
            beta = random.randint(1, 2)
            for j in range(self.num_vars):
                T[self.num_vars - 1, j] = alpha * T[0, j] + beta * T[1, j]

            # 检查最后一行是否为零向量
            last_row_zero = all(T[self.num_vars - 1, j] == 0 for j in range(self.num_vars))

            if not last_row_zero and T.det() == 0:
                break

        # 构造标准形 - 确保有n个平方项
        y_vars = symbols(f'y1:{self.num_vars + 1}')
        standard_form = sum(random.randint(1, 3) * y_vars[i] ** 2 for i in range(self.num_vars))

        # 将标准形转换回x变量
        substitution = {}
        for i in range(self.num_vars):
            substitution[y_vars[i]] = sum(T[i, j] * self.vars[j] for j in range(self.num_vars))

        poly = standard_form.subs(substitution)

        return poly, "陷阱题", T

    def generate_easy_problem(self):
        """生成送分题（已配好且可逆）"""
        # 构造一个可逆的变换矩阵
        while True:
            T = sp.Matrix([[random.randint(-2, 2) for _ in range(self.num_vars)]
                           for _ in range(self.num_vars)])
            if T.det() != 0:
                break

        # 构造标准形
        y_vars = symbols(f'y1:{self.num_vars + 1}')
        standard_form = sum(random.randint(1, 3) * y_vars[i] ** 2 for i in range(self.num_vars))

        # 将标准形转换回x变量
        substitution = {}
        for i in range(self.num_vars):
            substitution[y_vars[i]] = sum(T[i, j] * self.vars[j] for j in range(self.num_vars))

        poly = standard_form.subs(substitution)

        return poly, "送分题", T

    def generate_problem(self):
        """随机生成一个问题"""
        problem_type = random.choice(["常规题", "陷阱题", "送分题"])
        if problem_type == "常规题":
            return self.generate_regular_problem()
        elif problem_type == "陷阱题":
            return self.generate_trap_problem()
        else:
            return self.generate_easy_problem()

    def complete_square(self, poly):
        """
        使用配方法将二次型化为标准形。
        返回 (标准形, 变换矩阵)
        """
        n = self.num_vars
        x = self.vars

        # 首先展开多项式
        poly_expanded = sp.expand(poly)

        # 提取系数矩阵
        A = sp.zeros(n)
        for i in range(n):
            for j in range(n):
                if i == j:
                    # 平方项系数
                    A[i, j] = poly_expanded.coeff(x[i] ** 2)
                else:
                    # 交叉项系数（除以2，因为交叉项会出现两次）
                    coeff = poly_expanded.coeff(x[i] * x[j])
                    A[i, j] = coeff / 2
                    A[j, i] = coeff / 2

        # 使用配方法计算变换矩阵
        T = sp.eye(n)

        # 对每个变量进行配方
        for i in range(n):
            # 如果当前变量的平方项系数为0，跳过
            if A[i, i] == 0:
                continue

            # 创建当前步骤的变换矩阵
            T_step = sp.eye(n)

            # 更新变换矩阵 - 只更新当前行
            for j in range(i + 1, n):
                if A[i, j] != 0:
                    T_step[i, j] = -A[i, j] / A[i, i]

            # 应用变换到系数矩阵
            A = T_step.T * A * T_step

            # 更新总变换矩阵
            T = T * T_step

        # 计算标准形
        y_vars = symbols(f'y1:{n + 1}')
        substitution = {}
        for i in range(n):
            substitution[x[i]] = sum(T[i, j] * y_vars[j] for j in range(n))

        standard_form = poly_expanded.subs(substitution)
        standard_form = sp.expand(standard_form)

        return standard_form, T

    def solve_problem(self, poly, problem_type, T=None):
        """解决问题并提供解析和正确答案"""
        solution = f"题目类型: {problem_type}\n\n"
        solution += f"二次型: {poly}\n\n"
        solution += "解析:\n"
        if problem_type == '送分题':
            solution += "1. 这是一个送分题，已经配好\n"
            solution += "2. 变换矩阵可逆\n"
            solution += f"3. 变换矩阵: {T.inv()}\n"
            solution += f"4. 行列式: {T.det()} (≠0，变换可逆)\n"
            solution += "5. 可直接使用该变换\n\n"
        else:
            if problem_type == "常规题":
                solution += "1. 这是一个需要配方的常规题\n"
                solution += "2. 使用配方法将二次型化为标准形\n"
                solution += "3. 寻找可逆线性变换\n\n"
            else:
                solution += "1. 这是一个陷阱题，看起来已经配好\n"
                solution += "2. 表面上有与未知数个数相同的平方项\n"
                solution += "3. 但变换矩阵行列式为0，变换不可逆\n"
                solution += f"4. 给定变换矩阵: {T}\n"
                solution += f"5. 给定变换矩阵行列式: {T.det()} (=0，变换不可逆)\n"
                solution += "6. 需要重新寻找可逆变换\n\n"
            # 使用配方法求解
            standard_form, correct_T = self.complete_square(poly)
            solution += f"可逆线性变换矩阵:\n{correct_T}\n"
            solution += f"变换矩阵行列式: {correct_T.det()} (≠0，变换可逆)\n"
        return solution


# 使用示例
if __name__ == "__main__":
    generator = QuadraticFormGenerator(3)

    print("二次型标准化（配方法）习题生成器")
    print("=" * 50)

    # 生成5个问题
    for i_ in range(5):
        print(f"\n问题 {i_ + 1}:")
        p, pt, T_ = generator.generate_problem()
        print(f"用拉格朗日配方法将下列二次型化为标准形，并写出所用的可逆线性变换:")
        print(f"f(x) = {p}")

        # 显示答案和解析
        input("\n按回车键查看答案和解析...")
        s = generator.solve_problem(p, pt, T_)
        print(s)
        print("-" * 50)
