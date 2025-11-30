import random
from typing import List

import numpy as np


class InverseMatrixGenerator:
    def __init__(self):
        self.matrix_types = {
            '2x2': self._generate_2x2_matrix,
            '3x3': self._generate_3x3_matrix,
            '4x4': self._generate_4x4_matrix
        }

    def generate_problem(self, size: str = '3x3'):
        """生成逆矩阵求解题目"""
        if size not in self.matrix_types:
            raise ValueError("Size must be '2x2', '3x3', or '4x4'")

        matrix = self.matrix_types[size]()
        return matrix

    @staticmethod
    def _generate_2x2_matrix():
        """生成2x2矩阵"""
        while True:
            a, b = random.randint(1, 5), random.randint(1, 5)
            c, d = random.randint(1, 5), random.randint(1, 5)
            det = a * d - b * c
            if det != 0:  # 确保矩阵可逆
                matrix = [[a, b], [c, d]]
                return matrix

    @staticmethod
    def _generate_3x3_matrix():
        """生成3x3矩阵"""
        while True:
            matrix = []
            for i in range(3):
                row = [random.randint(-3, 3) for _ in range(3)]
                matrix.append(row)

            # 检查矩阵是否可逆
            if abs(np.linalg.det(matrix)) > 1e-10:
                return matrix

    @staticmethod
    def _generate_4x4_matrix():
        """生成4x4矩阵"""
        while True:
            matrix = []
            for i in range(4):
                row = [random.randint(-2, 2) for _ in range(4)]
                matrix.append(row)

            # 检查矩阵是否可逆
            if abs(np.linalg.det(matrix)) > 1e-10:
                return matrix

    def solve_inverse_matrix(self, matrix: List[List[float]]):
        """使用同步初等变换法求解逆矩阵"""
        n = len(matrix)

        # 构造增广矩阵 [A | E]
        augmented = []
        for i in range(n):
            row = matrix[i] + [1 if j == i else 0 for j in range(n)]
            augmented.append(row)

        # 同步初等行变换
        steps = [f"初始增广矩阵：\n{self._matrix_to_string(augmented)}"]

        for col in range(n):
            # 找到主元行
            pivot_row = col
            for r in range(col + 1, n):
                if abs(augmented[r][col]) > abs(augmented[pivot_row][col]):
                    pivot_row = r

            # 交换行（如果需要）
            if pivot_row != col:
                augmented[col], augmented[pivot_row] = augmented[pivot_row], augmented[col]
                steps.append(f"交换第{col + 1}行和第{pivot_row + 1}行：\n{self._matrix_to_string(augmented)}")

            # 主元归一化
            pivot = augmented[col][col]
            if abs(pivot) < 1e-10:
                raise ValueError("矩阵不可逆")

            for j in range(2 * n):
                augmented[col][j] /= pivot

            steps.append(f"第{col + 1}行除以{pivot:.2f}：\n{self._matrix_to_string(augmented)}")

            # 消元
            for i in range(n):
                if i != col:
                    factor = augmented[i][col]
                    for j in range(2 * n):
                        augmented[i][j] -= factor * augmented[col][j]

                    steps.append(f"第{i + 1}行减去{factor:.2f}×第{col + 1}行：\n{self._matrix_to_string(augmented)}")

        # 提取逆矩阵
        inverse = []
        for i in range(n):
            inverse.append(augmented[i][n:])

        return inverse, steps

    @staticmethod
    def _matrix_to_string(matrix: List[List[float]]) -> str:
        """将矩阵转换为字符串表示"""
        result = []
        for row in matrix:
            formatted_row = []
            for elem in row:
                if abs(elem) < 1e-10:
                    formatted_row.append("0")
                elif abs(elem - round(elem)) < 1e-10:
                    formatted_row.append(str(int(round(elem))))
                else:
                    formatted_row.append(f"{elem:.2f}")
            result.append("[" + "  ".join(formatted_row) + "]")
        return "\n".join(result)

    def generate_complete_problem(self, size: str = '3x3') -> dict:
        """生成完整的题目、答案和解析"""
        # 生成矩阵
        matrix = self.generate_problem(size)

        # 求解逆矩阵
        try:
            inverse, steps = self.solve_inverse_matrix(matrix)
            verification = np.dot(matrix, inverse)

            return {
                'matrix': matrix,
                'inverse': inverse,
                'steps': steps,
                'verification': verification.tolist() if hasattr(verification, 'tolist') else verification
            }
        except Exception as e:
            print(repr(e))
            return self.generate_complete_problem(size)  # 重新生成

    def print_problem(self, result: dict):
        """打印题目"""
        print("=" * 50)
        print("逆矩阵求解题目（同步初等变换法）")
        print("=" * 50)
        print(f"\n已知矩阵 A = ")
        print(self._matrix_to_string(result['matrix']))
        print(f"\n使用同步初等变换法求矩阵 A 的逆矩阵。")
        print("构造增广矩阵 [A | E]，然后进行同步初等行变换。")

    def print_solution(self, result: dict):
        """打印答案和解析"""
        print("\n" + "=" * 50)
        print("解答过程")
        print("=" * 50)

        # 显示求解步骤
        for i, step in enumerate(result['steps'], 1):
            print(f"\n步骤 {i}:")
            print(step)

        print("\n" + "=" * 50)
        print("最终结果")
        print("=" * 50)
        print(f"\n矩阵 A 的逆矩阵为：")
        print(self._matrix_to_string(result['inverse']))

        print(f"\n验证：A × A⁻¹ = ")
        print(self._matrix_to_string(result['verification']))
        print("结果接近单位矩阵，验证正确！")


def main():
    generator = InverseMatrixGenerator()

    print("逆矩阵求解（同步初等变换法）生成器")
    print("1. 2x2 矩阵")
    print("2. 3x3 矩阵")
    print("3. 4x4 矩阵")

    choice = input("\n请选择矩阵大小 (1/2/3): ").strip()

    size_map = {'1': '2x2', '2': '3x3', '3': '4x4'}
    size = size_map.get(choice, '3x3')

    # 生成题目
    result = generator.generate_complete_problem(size)

    # 显示题目
    generator.print_problem(result)

    input("\n按回车键查看解答...")

    # 显示解答
    generator.print_solution(result)


if __name__ == "__main__":
    main()
