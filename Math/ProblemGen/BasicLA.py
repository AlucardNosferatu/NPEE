import random
import numpy as np
from fractions import Fraction

class LinearAlgebraProblemGenerator:
    def __init__(self):
        self.problem_types = {
            '1': '行列式化简与计算',
            '2': '非同步初等变换（求秩/阶梯形）', 
            '3': '同步初等变换（求逆/解方程组）'
        }
    
    def display_menu(self):
        """显示菜单"""
        print("\n" + "="*50)
        print("线性代数题目生成器")
        print("="*50)
        for key, value in self.problem_types.items():
            print(f"{key}. {value}")
        print("0. 退出程序")
        print("="*50)
    
    def generate_determinant_problem(self):
        """生成行列式化简与计算题目"""
        n = random.choice([3, 4])  # 3阶或4阶行列式
        matrix = self._generate_integer_matrix(n, n, -5, 5)
        
        # 计算正确答案
        det_value = np.linalg.det(matrix)
        
        problem = f"计算下列{ n}阶行列式的值：\n"
        problem += self._matrix_to_str(matrix)
        
        answer = f"行列式的值为：{det_value:.2f}"
        
        explanation = "解题步骤：\n"
        explanation += "1. 观察行列式特点，选择合适的化简方法\n"
        explanation += "2. 可以使用行变换或列变换化简\n"
        explanation += "3. 注意变换时行列式值的变化规律：\n"
        explanation += "   - 交换两行(列)：值变号\n"
        explanation += "   - 某行(列)乘以k：值乘以k\n"
        explanation += "   - 某行(列)的倍数加到另一行(列)：值不变\n"
        explanation += "4. 最终化为上三角行列式计算\n"
        
        return problem, answer, explanation
    
    def generate_rank_problem(self):
        """生成非同步初等变换求秩题目"""
        rows = random.choice([3, 4])
        cols = random.choice([3, 4, 5])
        matrix = self._generate_integer_matrix(rows, cols, -3, 3)
        
        # 计算秩
        rank = np.linalg.matrix_rank(matrix)
        
        problem = f"求下列矩阵的秩（化为行阶梯形）：\n"
        problem += self._matrix_to_str(matrix)
        
        answer = f"矩阵的秩为：{rank}"
        
        explanation = "解题步骤：\n"
        explanation += "1. 使用初等行变换将矩阵化为行阶梯形\n"
        explanation += "2. 行阶梯形特点：\n"
        explanation += "   - 零行在底部\n"
        explanation += "   - 非零行的首个非零元（主元）下方全为0\n"
        explanation += "3. 统计非零行的数量即为矩阵的秩\n"
        explanation += "注意：求秩时可以使用行变换和列变换，但解方程只能使用行变换\n"
        
        return problem, answer, explanation
    
    def generate_sync_transform_problem(self):
        """生成同步初等变换题目"""
        problem_type = random.choice(['inverse', 'equation'])
        
        if problem_type == 'inverse':
            return self._generate_inverse_problem()
        else:
            return self._generate_equation_problem()
    
    def _generate_inverse_problem(self):
        """生成求逆矩阵题目"""
        n = 3  # 3阶矩阵
        # 生成可逆矩阵
        while True:
            matrix = self._generate_integer_matrix(n, n, -3, 3)
            if np.linalg.det(matrix) != 0:
                break
        
        problem = f"用同步初等变换法求下列矩阵的逆矩阵：\n"
        problem += self._matrix_to_str(matrix)
        
        # 计算逆矩阵
        try:
            inv_matrix = np.linalg.inv(matrix)
            answer = "逆矩阵为：\n" + self._matrix_to_str(inv_matrix, decimal=True)
        except:
            answer = "该矩阵不可逆"
        
        explanation = "解题步骤：\n"
        explanation += "1. 构造增广矩阵 [A | E]\n"
        explanation += "2. 对增广矩阵进行同步初等行变换\n"
        explanation += "3. 将左侧A化为单位矩阵E\n"
        explanation += "4. 此时右侧即为逆矩阵A⁻¹\n"
        explanation += "关键：只能使用行变换，且变换要同步作用于整个增广矩阵\n"
        
        return problem, answer, explanation
    
    def _generate_equation_problem(self):
        """生成解线性方程组题目"""
        n = 3  # 3个方程，3个未知数
        A = self._generate_integer_matrix(n, n, -3, 3)
        # 确保方程组有解
        while np.linalg.det(A) == 0:
            A = self._generate_integer_matrix(n, n, -3, 3)
        
        b = self._generate_integer_matrix(n, 1, -5, 5)
        
        problem = "用同步初等变换法解下列线性方程组：\n"
        # 显示方程组
        variables = ['x', 'y', 'z']
        for i in range(n):
            equation = ""
            for j in range(n):
                if A[i][j] != 0:
                    if equation and A[i][j] > 0:
                        equation += " + "
                    elif equation and A[i][j] < 0:
                        equation += " - "
                    coeff = abs(A[i][j])
                    if coeff != 1:
                        equation += f"{coeff}"
                    equation += f"{variables[j]}"
            equation += f" = {b[i][0]}"
            problem += equation + "\n"
        
        # 计算解
        solution = np.linalg.solve(A, b)
        answer = "方程组的解为：\n"
        for i, var in enumerate(variables):
            answer += f"{var} = {solution[i][0]:.2f}\n"
        
        explanation = "解题步骤：\n"
        explanation += "1. 写出增广矩阵 [A | b]\n"
        explanation += "2. 使用初等行变换将增广矩阵化为行最简形\n"
        explanation += "3. 从行最简形直接读出方程组的解\n"
        explanation += "注意：只能使用行变换，不能使用列变换\n"
        explanation += "关键边界：解方程组时列变换会改变未知数的位置\n"
        
        return problem, answer, explanation
    
    def _generate_integer_matrix(self, rows, cols, min_val, max_val):
        """生成整数矩阵"""
        matrix = []
        for _ in range(rows):
            row = [random.randint(min_val, max_val) for _ in range(cols)]
            matrix.append(row)
        return matrix
    
    def _matrix_to_str(self, matrix, decimal=False):
        """将矩阵转换为字符串表示"""
        result = ""
        for row in matrix:
            if isinstance(row, (int, float, np.float64)):
                # 处理一维数组情况
                if decimal:
                    result += f"[{row:8.2f}]\n"
                else:
                    result += f"[{row:3d}]\n"
            else:
                row_str = "["
                for elem in row:
                    if decimal:
                        row_str += f"{elem:8.2f}"
                    else:
                        row_str += f"{elem:3d}"
                row_str += " ]\n"
                result += row_str
        return result
    
    def run(self):
        """运行主程序"""
        print("欢迎使用线性代数题目生成器！")
        
        while True:
            self.display_menu()
            choice = input("请选择题型编号（0-3）：").strip()
            
            if choice == '0':
                print("感谢使用，再见！")
                break
            
            if choice in self.problem_types:
                print("\n" + "="*50)
                print(f"生成题目：{self.problem_types[choice]}")
                print("="*50)
                
                if choice == '1':
                    problem, answer, explanation = self.generate_determinant_problem()
                elif choice == '2':
                    problem, answer, explanation = self.generate_rank_problem()
                elif choice == '3':
                    problem, answer, explanation = self.generate_sync_transform_problem()
                
                print("\n【题目】")
                print(problem)
                
                input("\n按回车键查看答案...")
                
                print("\n【答案】")
                print(answer)
                
                print("\n【解析与提示】")
                print(explanation)
                
                print("\n" + "="*50)
            else:
                print("无效选择，请重新输入！")
            
            continue_choice = input("\n是否继续生成题目？(y/n): ").strip().lower()
            if continue_choice != 'y':
                print("感谢使用，再见！")
                break

# 运行程序
if __name__ == "__main__":
    generator = LinearAlgebraProblemGenerator()
    generator.run()