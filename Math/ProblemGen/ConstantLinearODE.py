import random

import sympy as sp
from sympy import symbols, Function, Eq, exp, cos, sin, diff, dsolve


class ODESolver:
    def __init__(self):
        self.x = symbols('x')
        self.y = Function('y')(self.x)
        # 用于格式化的符号
        self.y_func = Function('y')

    @staticmethod
    def format_equation(equation):
        """格式化微分方程输出"""
        # 提取方程左右两边
        lhs = equation.lhs
        rhs = equation.rhs

        # 将导数表示为标准数学格式
        # 将Derivative(y(x), (x, n))转换为y^(n)
        lhs_str = str(lhs)

        # 替换导数表示
        import re

        # 替换一阶导数: Derivative(y(x), x) -> y'
        lhs_str = re.sub(r"Derivative\(y\(x\), x\)", "y'", lhs_str)

        # 替换二阶导数: Derivative(y(x), (x, 2)) -> y''
        lhs_str = re.sub(r"Derivative\(y\(x\), \(x, 2\)\)", "y''", lhs_str)

        # 替换三阶导数: Derivative(y(x), (x, 3)) -> y'''
        lhs_str = re.sub(r"Derivative\(y\(x\), \(x, 3\)\)", "y'''", lhs_str)

        # 替换y(x)为y
        lhs_str = re.sub(r"y\(x\)", "y", lhs_str)

        # 简化系数为1的情况
        lhs_str = re.sub(r"1\*", "", lhs_str)
        lhs_str = re.sub(r"\+ -", "- ", lhs_str)

        # 处理等号右边
        rhs_str = str(rhs)
        rhs_str = re.sub(r"y\(x\)", "y", rhs_str)
        rhs_str = re.sub(r"exp\(", "e^(", rhs_str)

        # 如果rhs_str以"e^(开头)，尝试简化指数中的x系数
        if "e^(" in rhs_str:
            # 提取指数内容
            match = re.search(r"e\^\((.*?)\)", rhs_str)
            if match:
                exp_content = match.group(1)
                # 尝试简化系数
                try:
                    exp_expr = sp.sympify(exp_content)
                    simplified = sp.simplify(exp_expr)
                    if simplified != exp_expr:
                        rhs_str = rhs_str.replace(exp_content, str(simplified))
                except:
                    pass

        return f"{lhs_str} = {rhs_str}"

    @staticmethod
    def format_solution(solution):
        """格式化解的输出"""
        sol_str = str(solution)

        # 简化表达式
        if isinstance(solution, sp.Equality):
            # 提取解
            sol_expr = solution.rhs

            # 简化表达式
            simplified_expr = sp.simplify(sol_expr)

            # 替换y(x)为y
            sol_str = f"y = {simplified_expr}"

            # 替换exp为e^
            sol_str = sol_str.replace("exp(", "e^(")

            # 替换C1, C2, C3为标准的常数表示
            sol_str = sol_str.replace("C1", "C₁")
            sol_str = sol_str.replace("C2", "C₂")
            sol_str = sol_str.replace("C3", "C₃")

        return sol_str

    def generate_random_equation(self, order=None):
        """生成随机常系数线性非齐次微分方程"""
        if order is None:
            order = random.choice([2, 3])

        # 随机生成系数
        if order == 2:
            p = random.choice([-3, -2, -1, 0, 1, 2, 3])
            q = random.choice([-3, -2, -1, 0, 1, 2, 3])
            coeffs = [p, q]
            left_side = diff(self.y, self.x, 2) + p * diff(self.y, self.x) + q * self.y
            order_str = "二阶"
        else:  # order == 3
            p = random.choice([-2, -1, 0, 1, 2])
            q = random.choice([-2, -1, 0, 1, 2])
            s = random.choice([-2, -1, 0, 1, 2])
            coeffs = [p, q, s]
            left_side = diff(self.y, self.x, 3) + p * diff(self.y, self.x, 2) + q * diff(self.y, self.x) + s * self.y
            order_str = "三阶"

        # 随机生成非齐次项
        f_x = self._generate_fx()

        # 构造方程
        equation = Eq(left_side, f_x)

        return equation, coeffs, f_x, order_str

    def _generate_fx(self):
        """生成随机非齐次项"""
        # 非齐次项类型
        fx_types = [
            'polynomial',
            'exponential',
            'trigonometric',
            'exponential_trig',
            'poly_exp',
            'poly_trig'
        ]
        fx_type = random.choice(fx_types)

        if fx_type == 'polynomial':
            # 多项式
            degree = random.randint(0, 3)
            coeffs = [random.choice([-2, -1, 1, 2]) for _ in range(degree + 1)]
            # 确保多项式不为零
            if all(c == 0 for c in coeffs):
                coeffs[0] = random.choice([1, 2])
            fx = sum(c * self.x ** i for i, c in enumerate(coeffs))

        elif fx_type == 'exponential':
            # 指数函数
            a = random.choice([1, 2])
            b = random.choice([-2, -1, 1, 2])
            fx = a * exp(b * self.x)

        elif fx_type == 'trigonometric':
            # 三角函数
            trig_func = random.choice([cos, sin])
            a = random.choice([1, 2])
            b = random.choice([1, 2, 3])
            fx = a * trig_func(b * self.x)

        elif fx_type == 'exponential_trig':
            # 指数乘以三角函数
            a = random.choice([1, 2])
            b = random.choice([-1, 1, 2])
            trig_func = random.choice([cos, sin])
            c = random.choice([1, 2])
            fx = a * exp(b * self.x) * trig_func(c * self.x)

        elif fx_type == 'poly_exp':
            # 多项式乘以指数
            degree = random.randint(0, 2)
            coeffs = [random.choice([1, 2]) for _ in range(degree + 1)]
            poly = sum(c * self.x ** i for i, c in enumerate(coeffs))
            b = random.choice([-1, 1, 2])
            fx = poly * exp(b * self.x)

        else:  # 'poly_trig'
            # 多项式乘以三角函数
            degree = random.randint(0, 2)
            coeffs = [random.choice([1, 2]) for _ in range(degree + 1)]
            poly = sum(c * self.x ** i for i, c in enumerate(coeffs))
            trig_func = random.choice([cos, sin])
            b = random.choice([1, 2])
            fx = poly * trig_func(b * self.x)

        return fx

    def solve_equation(self, equation):
        """使用SymPy的dsolve求解微分方程"""
        try:
            solution = dsolve(equation, self.y)
            return solution
        except Exception as e:
            return f"求解失败: {e}"

    def generate_problem_solution_pair(self):
        """生成一对题目和解答"""
        # 随机选择阶数
        order = random.choice([2, 3])

        # 生成方程
        equation, coeffs, f_x, order_str = self.generate_random_equation(order)

        # 求解
        solution = self.solve_equation(equation)

        # 格式化输出
        formatted_eq = self.format_equation(equation)

        if isinstance(solution, str):
            formatted_sol = solution
        else:
            formatted_sol = self.format_solution(solution)

        return {
            'order': order,
            'order_str': order_str,
            'equation': equation,
            'formatted_equation': formatted_eq,
            'solution': solution,
            'formatted_solution': formatted_sol
        }


# 主程序
if __name__ == "__main__":
    solver = ODESolver()

    print("=" * 70)
    print("常系数线性非齐次微分方程随机题目生成器")
    print("=" * 70)
    print()

    # 生成指定数量的题目
    num_problems = 5

    for i_ in range(num_problems):
        print(f"题目 {i_ + 1}:")
        print("-" * 70)

        # 生成一对题目和解答
        problem = solver.generate_problem_solution_pair()

        # 显示题目
        print(f"【{problem['order_str']}方程】")
        print(f"方程: {problem['formatted_equation']}")
        print()

        # 显示解答
        print("解答:")
        print(f"通解: {problem['formatted_solution']}")

        print("=" * 70)
        print()
        cmd = ''
        while cmd.lower() not in ['y', 'n']:
            cmd = input('继续？y/n')
        if cmd == 'n':
            break
    print("题目生成完毕！")
    print("=" * 70)
