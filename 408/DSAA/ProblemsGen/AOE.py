import random
from typing import List, Tuple, Dict

import numpy as np


class AOEQuestionGenerator:
    def __init__(self):
        self.activities = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        self.current_question = None

    @staticmethod
    def _ensure_connectivity(matrix: np.ndarray):
        """确保图是连通的"""
        n = len(matrix)
        visited = [False] * n

        def dfs(node):
            visited[node] = True
            for neighbor in range(n):
                if matrix[node][neighbor] > 0 and not visited[neighbor]:
                    dfs(neighbor)

        # 从节点0开始DFS
        dfs(0)

        # 如果有未访问的节点，添加边连接它们
        for i in range(1, n):
            if not visited[i]:
                # 随机连接到已访问的节点
                possible_sources = [j for j in range(n) if visited[j] and j < i]
                if possible_sources:
                    source = random.choice(possible_sources)
                    matrix[source][i] = random.randint(2, 8)

    def generate_adjacency_matrix(self, num_vertices: int = 6) -> np.ndarray:
        """生成AOE网的邻接矩阵 - 修复版本"""
        matrix = np.zeros((num_vertices, num_vertices), dtype=int)

        # 基础边确保连通性 - 创建一个主路径
        main_path_length = random.randint(3, num_vertices)
        main_path = random.sample(range(num_vertices), main_path_length)
        main_path.sort()

        # 为主路径添加边
        for idx in range(len(main_path) - 1):
            weight = random.randint(3, 10)
            matrix[main_path[idx]][main_path[idx + 1]] = weight

        # 添加额外的边 - 确保图有分支
        max_extra_edges = min(8, num_vertices * (num_vertices - 1) // 3)
        extra_edges = random.randint(3, max_extra_edges)

        edges_added = 0
        attempts = 0
        max_attempts = 50  # 防止无限循环

        while edges_added < extra_edges and attempts < max_attempts:
            i = random.randint(0, num_vertices - 2)
            j = random.randint(i + 1, num_vertices - 1)

            if matrix[i][j] == 0:  # 避免重复边
                weight = random.randint(1, 8)
                matrix[i][j] = weight
                edges_added += 1

            attempts += 1

        # 确保图是连通的（从0可以到达所有节点）
        self._ensure_connectivity(matrix)

        return matrix

    @staticmethod
    def topological_sort(matrix: np.ndarray) -> List[int]:
        """拓扑排序"""
        n = len(matrix)
        in_degree = [0] * n

        # 计算入度
        for i in range(n):
            for j in range(n):
                if matrix[i][j] > 0:
                    in_degree[j] += 1

        # 找到入度为0的顶点
        queue = [i for i in range(n) if in_degree[i] == 0]
        topo_order = []

        while queue:
            vertex = queue.pop(0)
            topo_order.append(vertex)

            for j in range(n):
                if matrix[vertex][j] > 0:
                    in_degree[j] -= 1
                    if in_degree[j] == 0:
                        queue.append(j)

        return topo_order

    def calculate_ve_vl(self, matrix: np.ndarray) -> Tuple[List[int], List[int]]:
        """计算ve和vl值"""
        n = len(matrix)
        topo_order = self.topological_sort(matrix)

        # 计算ve（最早发生时间）
        ve = [0] * n
        for i in topo_order:
            for j in range(n):
                if matrix[i][j] > 0:
                    if ve[j] < ve[i] + matrix[i][j]:
                        ve[j] = ve[i] + matrix[i][j]

        # 计算vl（最迟发生时间）
        vl = [ve[-1]] * n  # 初始化为ve的最大值
        for i in reversed(topo_order):
            for j in range(n):
                if matrix[i][j] > 0:
                    if vl[i] > vl[j] - matrix[i][j]:
                        vl[i] = vl[j] - matrix[i][j]

        return ve, vl

    @staticmethod
    def find_critical_activities(matrix: np.ndarray, ve: List[int], vl: List[int]) -> List[Tuple[int, int]]:
        """找出关键活动"""
        critical_activities = []
        n = len(matrix)

        for i in range(n):
            for j in range(n):
                if matrix[i][j] > 0:
                    earliest_start = ve[i]  # 活动最早开始时间
                    latest_start = vl[j] - matrix[i][j]  # 活动最迟开始时间
                    if earliest_start == latest_start:  # 关键活动条件
                        critical_activities.append((i, j))

        return critical_activities

    def generate_question(self) -> Dict:
        """生成完整的题目"""
        num_vertices = random.randint(5, 8)
        adj_matrix = self.generate_adjacency_matrix(num_vertices)
        ve, vl = self.calculate_ve_vl(adj_matrix)
        critical_activities = self.find_critical_activities(adj_matrix, ve, vl)

        question = {
            'adjacency_matrix': adj_matrix,
            've': ve,
            'vl': vl,
            'critical_activities': critical_activities,
            'topological_order': self.topological_sort(adj_matrix)
        }

        self.current_question = question
        return question

    @staticmethod
    def format_matrix(matrix: np.ndarray) -> str:
        """格式化邻接矩阵输出"""
        n = len(matrix)
        result = "   " + "  ".join(str(i) for i in range(n)) + "\n"
        for i in range(n):
            result += f"{i}  " + "  ".join(str(x) if x > 0 else "0" for x in matrix[i]) + "\n"
        return result

    def generate_exercise(self) -> str:
        """生成练习题"""
        if not self.current_question:
            self.generate_question()

        matrix = self.current_question['adjacency_matrix']

        exercise = f"""关键路径(AOE网)计算练习题：

给定以下AOE网的邻接矩阵（行→列，数字表示活动持续时间，0表示无边）：
{self.format_matrix(matrix)}

请计算：
1. 各顶点的最早发生时间(ve)和最迟发生时间(vl)
2. 找出所有的关键活动
3. 确定关键路径

步骤提示：
1. 先进行拓扑排序
2. 按拓扑顺序计算ve值
3. 按逆拓扑顺序计算vl值  
4. 根据ve和vl值判断关键活动
"""
        return exercise

    def generate_solution(self) -> str:
        """生成详细解答"""
        if not self.current_question:
            self.generate_question()

        q = self.current_question
        matrix = q['adjacency_matrix']

        solution = f"""详细解答：

1. 拓扑排序：
   拓扑序列: {q['topological_order']}

2. 计算ve值（最早发生时间）：
   ve[0] = 0
"""
        # 详细计算ve的过程
        n = len(matrix)
        for i in q['topological_order'][1:]:
            predecessors = [j for j in range(n) if matrix[j][i] > 0]
            if predecessors:
                max_val = max(q['ve'][j] + matrix[j][i] for j in predecessors)
                pred_str = ", ".join(f"ve[{j}]+{matrix[j][i]}" for j in predecessors)
                solution += f"   ve[{i}] = max({pred_str}) = {max_val}\n"

        solution += f"\n   ve数组: {q['ve']}\n\n"

        solution += "3. 计算vl值（最迟发生时间）：\n"
        solution += f"   vl[{n - 1}] = ve[{n - 1}] = {q['vl'][n - 1]}\n"

        for i in reversed(q['topological_order'][:-1]):
            successors = [j for j in range(n) if matrix[i][j] > 0]
            if successors:
                min_val = min(q['vl'][j] - matrix[i][j] for j in successors)
                succ_str = ", ".join(f"vl[{j}]-{matrix[i][j]}" for j in successors)
                solution += f"   vl[{i}] = min({succ_str}) = {min_val}\n"

        solution += f"\n   vl数组: {q['vl']}\n\n"

        solution += "4. 判断关键活动：\n"
        solution += "   关键活动条件：e(i) = l(i)，其中 e(i) = ve[i], l(i) = vl[j] - weight(i,j)\n"

        for i in range(n):
            for j in range(n):
                if matrix[i][j] > 0:
                    earliest_start = q['ve'][i]
                    latest_start = q['vl'][j] - matrix[i][j]
                    is_critical = "✓" if (i, j) in q['critical_activities'] else "✗"
                    solution += f"   活动({i}→{j}): e={earliest_start}, l={latest_start} {is_critical}\n"

        solution += f"\n5. 关键活动: {q['critical_activities']}\n"

        # 构建关键路径
        critical_path = []
        if q['critical_activities']:
            current = 0
            critical_path.append(current)
            while True:
                next_verts = [j for (i, j) in q['critical_activities'] if i == current]
                if not next_verts:
                    break
                current = next_verts[0]  # 取第一个关键活动
                critical_path.append(current)
                if current == n - 1:
                    break

        solution += f"6. 关键路径: {' → '.join(map(str, critical_path))}\n"
        solution += f"   总工期: {q['ve'][-1]}"

        return solution


def main():
    generator = AOEQuestionGenerator()

    print("=" * 60)
    print("关键路径(AOE网)计算复习题目生成器")
    print("=" * 60)

    while True:
        print("\n选择操作:")
        print("1. 生成新题目")
        print("2. 显示答案和解析")
        print("3. 退出")

        choice = input("请输入选择 (1-3): ").strip()

        if choice == '1':
            generator.generate_question()
            exercise = generator.generate_exercise()
            print("\n" + "=" * 50)
            print("新题目已生成!")
            print("=" * 50)
            print(exercise)

        elif choice == '2':
            if generator.current_question:
                solution = generator.generate_solution()
                print("\n" + "=" * 50)
                print("答案和解析:")
                print("=" * 50)
                print(solution)
            else:
                print("请先生成题目!")

        elif choice == '3':
            print("再见!")
            break

        else:
            print("无效输入，请重新选择!")


if __name__ == "__main__":
    main()
