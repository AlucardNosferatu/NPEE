import random

from sympy import symbols, Function, Eq, exp, cos, sin, diff, dsolve


class ODESolver:
    def __init__(self):
        self.x = symbols('x')
        self.y = Function('y')(self.x)

    def generate_random_equation(self, order=2):
        """生成随机常系数线性非齐次微分方程"""
        # 随机生成系数
        if order == 2:
            p = random.randint(-3, 3)
            q = random.randint(-3, 3)
            coeffs = [p, q]
            left_side = diff(self.y, self.x, 2) + p * diff(self.y, self.x) + q * self.y
        else:  # order == 3
            p = random.randint(-3, 3)
            q = random.randint(-3, 3)
            s = random.randint(-3, 3)
            coeffs = [p, q, s]
            left_side = diff(self.y, self.x, 3) + p * diff(self.y, self.x, 2) + q * diff(self.y, self.x) + s * self.y

        # 随机生成非齐次项
        f_x = self._generate_fx()

        # 构造方程
        equation = Eq(left_side, f_x)

        return equation, coeffs, f_x

    def _generate_fx(self):
        """生成随机非齐次项"""
        fx_types = ['polynomial', 'exponential', 'trigonometric', 'combined']
        fx_type = random.choice(fx_types)

        if fx_type == 'polynomial':
            # 多项式
            degree = random.randint(0, 3)
            coeffs = [random.randint(-3, 3) for _ in range(degree + 1)]
            fx = sum(c * self.x ** i for i, c in enumerate(coeffs))

        elif fx_type == 'exponential':
            # 指数函数
            a = random.randint(-2, 2)
            if a == 0:
                a = 1
            b = random.randint(-2, 2)
            if b == 0:
                b = 1
            fx = a * exp(b * self.x)

        elif fx_type == 'trigonometric':
            # 三角函数
            trig_func = random.choice([cos, sin])
            a = random.randint(-2, 2)
            if a == 0:
                a = 1
            b = random.randint(1, 3)
            fx = a * trig_func(b * self.x)

        else:  # combined
            # 组合形式
            types = random.sample(['poly', 'exp', 'trig'], 2)
            terms = []

            if 'poly' in types:
                degree = random.randint(0, 2)
                coeffs = [random.randint(-2, 2) for _ in range(degree + 1)]
                poly_term = sum(c * self.x ** i for i, c in enumerate(coeffs))
                terms.append(poly_term)

            if 'exp' in types:
                a = random.randint(1, 2)
                b = random.randint(1, 2)
                exp_term = a * exp(b * self.x)
                terms.append(exp_term)

            if 'trig' in types:
                trig_func = random.choice([cos, sin])
                a = random.randint(1, 2)
                b = random.randint(1, 2)
                trig_term = a * trig_func(b * self.x)
                terms.append(trig_term)

            fx = sum(terms)

        return fx

    def solve_equation(self, equation):
        """使用SymPy的dsolve求解微分方程"""
        try:
            solution = dsolve(equation, self.y)
            return solution
        except Exception as e:
            return f"求解失败: {e}"

    def run_test_cases(self, num_cases=2):
        """运行测试用例"""
        results = []

        for i in range(num_cases):
            order = random.choice([2, 3])
            print(f"\n{'=' * 60}")
            print(f"测试用例 {i + 1}: {'二阶' if order == 2 else '三阶'}常系数线性非齐次微分方程")
            print('=' * 60)

            # 生成方程
            equation, coeffs, f_x = self.generate_random_equation(order)
            print(f"方程: {equation}")

            # 求解
            solution = self.solve_equation(equation)
            print(f"解: {solution}")

            results.append({
                'order': order,
                'equation': equation,
                'solution': solution
            })

        return results

    def solve_specific_equation(self, order, coefficients, f_x):
        """求解特定的微分方程"""
        # 构建方程
        if order == 2:
            p, q = coefficients
            left_side = diff(self.y, self.x, 2) + p * diff(self.y, self.x) + q * self.y
        else:  # order == 3
            p, q, s = coefficients
            left_side = diff(self.y, self.x, 3) + p * diff(self.y, self.x, 2) + q * diff(self.y, self.x) + s * self.y

        equation = Eq(left_side, f_x)

        print(f"\n{'=' * 60}")
        print(f"求解{'二阶' if order == 2 else '三阶'}常系数线性非齐次微分方程")
        print('=' * 60)
        print(f"方程: {equation}")

        solution = self.solve_equation(equation)
        print(f"解: {solution}")

        return solution


# 主程序
if __name__ == "__main__":
    solver = ODESolver()

    print("常系数线性非齐次微分方程求解器")
    print("使用SymPy内置dsolve函数直接求解")
    print("=" * 60)

    # 运行随机测试用例
    solver.run_test_cases(2)

    # 固定测试用例（原问题中的示例）
    print(f"\n{'=' * 60}")
    print("固定测试用例（原问题中的示例）")
    print('=' * 60)

    # 测试用例1: 二阶方程 y'' + 2y' + 2y = e^(-x) + x*cos(x)
    # 注意：由于SymPy可以处理复杂非齐次项，我们直接求解整个方程
    print("\n测试用例1: y'' + 2y' + 2y = e^(-x) + x*cos(x)")
    f1 = exp(-solver.x) + solver.x * cos(solver.x)
    solver.solve_specific_equation(2, [2, 2], f1)

    # 测试用例2: 三阶方程 y''' - y'' + y' - y = x² + e^x*sin(x)
    print("\n测试用例2: y''' - y'' + y' - y = x² + e^x*sin(x)")
    f2 = solver.x ** 2 + exp(solver.x) * sin(solver.x)
    solver.solve_specific_equation(3, [-1, 1, -1], f2)

    print(f"\n{'=' * 60}")
    print("求解完成!")
    print('=' * 60)
