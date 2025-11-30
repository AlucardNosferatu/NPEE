import random

import numpy as np
import sympy as sp
from sympy import Matrix, symbols, latex


# noinspection PyPep8Naming
class EigenProblemGenerator:
    def __init__(self, size=3):
        self.size = size
        self.lam = symbols('λ')

    def generate_type1(self):
        """类型1: 各特征值代数重数为1"""
        # 生成不同的特征值
        eigenvalues = random.sample(range(-3, 4), self.size)
        while len(set(eigenvalues)) < self.size:
            eigenvalues = random.sample(range(-3, 4), self.size)

        D = sp.diag(*eigenvalues)
        P = self._generate_invertible_matrix()
        A = P * D * P.inv()

        return A, eigenvalues

    def generate_type2(self):
        """类型2: 代数重数2以上，几何重数满"""
        # 至少有一个特征值代数重数>=2，但几何重数等于代数重数
        eigenvalues = []
        # 确保至少有一个重根
        repeated_val = random.randint(-2, 2)
        multiplicity = random.randint(2, self.size - 1)
        eigenvalues.extend([repeated_val] * multiplicity)

        # 添加其他不同的特征值
        remaining = self.size - multiplicity
        other_vals = [x for x in range(-3, 4) if x != repeated_val]
        eigenvalues.extend(random.sample(other_vals, remaining))

        D = sp.diag(*eigenvalues)
        P = self._generate_invertible_matrix()
        A = P * D * P.inv()

        return A, eigenvalues

    def generate_type3(self):
        """类型3: 代数重数2以上，几何重数未满(不可对角化)"""
        # 创建若当块确保不可对角化
        J_blocks = []
        eigenvalues = []

        # 至少一个若当块大小>=2
        jordan_size = random.randint(2, self.size)
        jordan_val = random.randint(-2, 2)

        J_block = self._create_jordan_block(jordan_size, jordan_val)
        J_blocks.append(J_block)
        eigenvalues.extend([jordan_val] * jordan_size)

        # 添加其他对角块
        remaining = self.size - jordan_size
        if remaining > 0:
            other_vals = [x for x in range(-3, 4) if x != jordan_val]
            vals = random.sample(other_vals, remaining)
            eigenvalues.extend(vals)
            for val in vals:
                J_blocks.append(Matrix([[val]]))

        # 构建若当标准型
        J = self._block_diag(*J_blocks)
        P = self._generate_invertible_matrix()
        A = P * J * P.inv()

        return A, eigenvalues

    def _generate_invertible_matrix(self):
        """生成可逆矩阵"""
        while True:
            P = Matrix(np.random.randint(-3, 4, (self.size, self.size)))
            if P.det() != 0:
                return P

    @staticmethod
    def _create_jordan_block(size, eigenvalue):
        """创建若当块"""
        J = sp.zeros(size, size)
        for i in range(size):
            J[i, i] = eigenvalue
            if i < size - 1:
                J[i, i + 1] = 1
        return J

    @staticmethod
    def _block_diag(*blocks):
        """构建块对角矩阵"""
        result = sp.zeros(0, 0)
        for block in blocks:
            rows, cols = result.shape
            block_rows, block_cols = block.shape
            new_result = sp.zeros(rows + block_rows, cols + block_cols)
            for i in range(rows):
                for j in range(cols):
                    new_result[i, j] = result[i, j]
            for i in range(block_rows):
                for j in range(block_cols):
                    new_result[rows + i, cols + j] = block[i, j]
            result = new_result
        return result

    def solve_eigenproblem(self, A):
        """求解特征问题"""
        # 特征多项式
        char_poly = A.charpoly(self.lam)

        # 特征值及其代数重数
        eigenvals = A.eigenvals()

        # 几何重数和特征向量
        eigenvects = A.eigenvects()

        # 可对角化性
        is_diagonalizable = A.is_diagonalizable()

        return {
            'characteristic_poly': char_poly,
            'eigenvalues': eigenvals,
            'eigenvectors': eigenvects,
            'is_diagonalizable': is_diagonalizable
        }

    def generate_problem(self, problem_type=None):
        """生成完整问题"""
        if problem_type is None:
            problem_type = random.choice([1, 2, 3])

        if problem_type == 1:
            A, true_eigenvalues = self.generate_type1()
            description = "各特征值代数重数为1"
        elif problem_type == 2:
            A, true_eigenvalues = self.generate_type2()
            description = "存在代数重数大于1的特征值，但几何重数等于代数重数"
        else:
            A, true_eigenvalues = self.generate_type3()
            description = "存在代数重数大于1的特征值，且几何重数小于代数重数"

        # 简化矩阵元素
        A = A.applyfunc(lambda x: x if abs(x) <= 10 else x / 2)
        A = A.applyfunc(sp.simplify)

        solution = self.solve_eigenproblem(A)

        return {
            'matrix': A,
            'description': description,
            'type': problem_type,
            'true_eigenvalues': true_eigenvalues,
            'solution': solution
        }


def print_problem(problem):
    """打印问题"""
    print("=" * 60)
    print(f"题目类型: {problem['description']}")
    print("=" * 60)
    print(f"给定矩阵 A = ")
    sp.pprint(problem['matrix'])
    print("\n要求:")
    print("1. 求矩阵A的所有特征值及其代数重数")
    print("2. 求每个特征值的几何重数")
    print("3. 判断矩阵是否可对角化")
    print("4. 求每个特征值对应的特征向量")
    print("=" * 60)


# noinspection PyPep8Naming
def print_solution(problem):
    """打印解答"""
    print("\n" + "=" * 60)
    print("解答:")
    print("=" * 60)

    sol = problem['solution']
    A = problem['matrix']
    _ = A
    print(f"1. 特征多项式:")
    print(f"   |λE - A| = {sol['characteristic_poly'].as_expr()}")

    print(f"\n2. 特征值及其代数重数:")
    for eigenval, multiplicity in sol['eigenvalues'].items():
        print(f"   λ = {eigenval}, 代数重数: {multiplicity}")

    print(f"\n3. 几何重数和可对角化性:")
    total_alg_mult = sum(sol['eigenvalues'].values())
    total_geo_mult = 0

    for eigenval, multiplicity, vectors in sol['eigenvectors']:
        geo_mult = len(vectors)
        total_geo_mult += geo_mult
        print(f"   λ = {eigenval}: 代数重数={multiplicity}, 几何重数={geo_mult}")
        if multiplicity == geo_mult:
            print(f"   ✓ 几何重数等于代数重数")
        else:
            print(f"   ✗ 几何重数小于代数重数")

    print(f"\n4. 可对角化判断:")
    if sol['is_diagonalizable']:
        print(f"   ✓ 矩阵可对角化 (总代数重数={total_alg_mult}, 总几何重数={total_geo_mult})")
    else:
        print(f"   ✗ 矩阵不可对角化 (总代数重数={total_alg_mult}, 总几何重数={total_geo_mult})")

    print(f"\n5. 特征向量:")
    for i, (eigenval, multiplicity, vectors) in enumerate(sol['eigenvectors']):
        print(f"   特征值 λ = {eigenval} 对应的特征向量:")
        for j, vec in enumerate(vectors):
            print(f"     v{i + 1}_{j + 1} = ", end="")
            sp.pprint(vec)

        # 显示齐次方程组
        print(f"   对应的齐次方程组 ( ({eigenval}E - A)x = 0 ) 的解")


def generate_text_output(problem):
    """生成纯文本格式的输出，适合直接使用"""
    output = ["=" * 60, f"题目类型: {problem['description']}", "=" * 60, "给定矩阵 A = ", str(problem['matrix']),
              "\n要求:", "1. 求矩阵A的所有特征值及其代数重数", "2. 求每个特征值的几何重数", "3. 判断矩阵是否可对角化",
              "4. 求每个特征值对应的特征向量", "=" * 60]

    # 解答部分
    sol = problem['solution']
    output.append("\n解答:")
    output.append("=" * 60)

    output.append("1. 特征多项式:")
    output.append(f"   |λE - A| = {sol['characteristic_poly'].as_expr()}")

    output.append("\n2. 特征值及其代数重数:")
    for eigenval, multiplicity in sol['eigenvalues'].items():
        output.append(f"   λ = {eigenval}, 代数重数: {multiplicity}")

    output.append("\n3. 几何重数和可对角化性:")
    total_alg_mult = sum(sol['eigenvalues'].values())
    total_geo_mult = 0

    for eigenval, multiplicity, vectors in sol['eigenvectors']:
        geo_mult = len(vectors)
        total_geo_mult += geo_mult
        output.append(f"   λ = {eigenval}: 代数重数={multiplicity}, 几何重数={geo_mult}")
        if multiplicity == geo_mult:
            output.append(f"   ✓ 几何重数等于代数重数")
        else:
            output.append(f"   ✗ 几何重数小于代数重数")

    output.append("\n4. 可对角化判断:")
    if sol['is_diagonalizable']:
        output.append(f"   ✓ 矩阵可对角化 (总代数重数={total_alg_mult}, 总几何重数={total_geo_mult})")
    else:
        output.append(f"   ✗ 矩阵不可对角化 (总代数重数={total_alg_mult}, 总几何重数={total_geo_mult})")

    output.append("\n5. 特征向量:")
    for i, (eigenval, multiplicity, vectors) in enumerate(sol['eigenvectors']):
        output.append(f"   特征值 λ = {eigenval} 对应的特征向量:")
        for j, vec in enumerate(vectors):
            output.append(f"     v{i + 1}_{j + 1} = {vec}")
        output.append(f"   对应的齐次方程组 ( ({eigenval}E - A)x = 0 ) 的解")

    return "\n".join(output)


def generate_simple_latex(problem):
    """生成简化的LaTeX代码，避免复杂的环境"""
    latex_parts = ["\\section*{特征值与特征向量问题}", f"\\textbf{{题目类型:}} {problem['description']}\\\\",
                   "\\textbf{给定矩阵:}\\\\", "$A = " + latex(problem['matrix']) + "$\\\\", "\\textbf{要求:}\\\\",
                   "1. 求矩阵A的所有特征值及其代数重数\\\\", "2. 求每个特征值的几何重数\\\\",
                   "3. 判断矩阵是否可对角化\\\\", "4. 求每个特征值对应的特征向量\\\\"]

    # 题目部分

    # 解答部分
    sol = problem['solution']
    latex_parts.append("\\section*{解答}")

    latex_parts.append("\\textbf{1. 特征多项式:}\\\\")
    latex_parts.append("$|\\lambda E - A| = " + latex(sol['characteristic_poly'].as_expr()) + "$\\\\")

    latex_parts.append("\\textbf{2. 特征值及其代数重数:}\\\\")
    for eigenval, multiplicity in sol['eigenvalues'].items():
        latex_parts.append(f"$\\lambda = {eigenval}$, 代数重数: ${multiplicity}$\\\\")

    latex_parts.append("\\textbf{3. 几何重数和可对角化性:}\\\\")
    for eigenval, multiplicity, vectors in sol['eigenvectors']:
        geo_mult = len(vectors)
        latex_parts.append(f"$\\lambda = {eigenval}$: 代数重数$={multiplicity}$, 几何重数$={geo_mult}$\\\\")
        if multiplicity == geo_mult:
            latex_parts.append("✓ 几何重数等于代数重数\\\\")
        else:
            latex_parts.append("✗ 几何重数小于代数重数\\\\")

    latex_parts.append("\\textbf{4. 可对角化判断:}\\\\")
    if sol['is_diagonalizable']:
        latex_parts.append("✓ 矩阵可对角化\\\\")
    else:
        latex_parts.append("✗ 矩阵不可对角化\\\\")

    latex_parts.append("\\textbf{5. 特征向量:}\\\\")
    for i, (eigenval, multiplicity, vectors) in enumerate(sol['eigenvectors']):
        latex_parts.append(f"特征值 $\\lambda = {eigenval}$ 对应的特征向量:\\\\")
        for j, vec in enumerate(vectors):
            latex_parts.append(f"$v_{{{i + 1},{j + 1}}} = " + latex(vec) + "$\\\\")
        latex_parts.append(f"对应的齐次方程组 $( {eigenval}E - A )x = 0$ 的解\\\\")

    return "\n".join(latex_parts)


# noinspection PyPep8Naming
def solve_eigenproblem_fixed(self, A):
    """求解特征问题 - 修复版本"""
    # 特征多项式
    char_poly = A.charpoly(self.lam)

    # 特征值及其代数重数
    eigenvals = A.eigenvals()

    # 几何重数和特征向量
    eigenvects = A.eigenvects()

    # 可对角化性
    is_diagonalizable = A.is_diagonalizable()

    return {
        'characteristic_poly': char_poly,  # 统一键名
        'eigenvalues': eigenvals,
        'eigenvectors': eigenvects,
        'is_diagonalizable': is_diagonalizable
    }


# 使用示例
if __name__ == "__main__":
    generator = EigenProblemGenerator(size=3)

    print("特征值与特征向量题目生成器")
    print("生成3种不同类型的题目...\n")

    # 替换原方法
    EigenProblemGenerator.solve_eigenproblem = solve_eigenproblem_fixed

    # 生成三种类型的题目
    for i_ in range(3):
        p = generator.generate_problem(problem_type=i_ + 1)
        print_problem(p)
        print_solution(p)
        print("\n" + "=" * 60)
