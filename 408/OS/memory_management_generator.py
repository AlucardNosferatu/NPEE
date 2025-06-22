import random


class MemoryManagementProblemGenerator:
    def __init__(self):
        # 常见页面大小，单位为字节
        self.page_sizes = [1024, 2048, 4096, 8192]
        # 常见物理块数量
        self.frame_counts = [3, 4, 5, 6]
        # 页面访问序列的长度范围
        self.access_sequence_length = (20, 30)
        # 页号和段号的范围
        self.page_segment_range = (0, 9)
        # 段大小的范围，单位为字节
        self.segment_size_range = (1000, 5000)
        # 逻辑地址的范围
        self.logical_address_range = (0, 65535)

    def generate_page_replacement_problem(self, algorithm=None):
        """生成页面置换算法问题"""
        if algorithm is None:
            algorithm = random.choice(['OPT', 'LRU', 'FIFO'])

        frame_count = random.choice(self.frame_counts)
        sequence_length = random.randint(*self.access_sequence_length)
        page_sequence = [random.randint(0, 9) for _ in range(sequence_length)]

        problem = {
            'type': 'page_replacement',
            'algorithm': algorithm,
            'frame_count': frame_count,
            'page_sequence': page_sequence
        }

        solution = self._solve_page_replacement(problem)
        return problem, solution

    @staticmethod
    def _solve_page_replacement(problem):
        """解决页面置换问题"""
        algorithm = problem['algorithm']
        frame_count = problem['frame_count']
        page_sequence = problem['page_sequence']

        frames = []
        page_faults = 0
        replacement_steps = []

        for i, page in enumerate(page_sequence):
            # 如果页面不在内存中，发生缺页
            if page not in frames:
                page_faults += 1

                # 如果内存已满，需要置换
                if len(frames) == frame_count:
                    if algorithm == 'OPT':
                        # 最优置换，置换未来最长时间不会使用的页面
                        future_usage = [page_sequence[i + 1:].index(p)
                                        if p in page_sequence[i + 1:]
                                        else float('inf')
                                        for p in frames]
                        replace_index = future_usage.index(max(future_usage))
                        replaced_page = frames.pop(replace_index)
                    else:
                        # 先进先出，置换最先进入的页面
                        # 最近最少使用，置换最久未使用的页面
                        replaced_page = frames.pop(0)

                    frames.append(page)
                    replacement_steps.append({
                        'step': i,
                        'page': page,
                        'replaced': replaced_page,
                        'frames': frames.copy()
                    })
                else:
                    # 内存未满，直接加入
                    frames.append(page)
                    replacement_steps.append({
                        'step': i,
                        'page': page,
                        'replaced': None,
                        'frames': frames.copy()
                    })
            else:
                # 页面已在内存中
                if algorithm == 'LRU':
                    # 将该页面移到frames末尾，表示最近使用
                    frames.remove(page)
                    frames.append(page)

                replacement_steps.append({
                    'step': i,
                    'page': page,
                    'replaced': page,
                    'frames': frames.copy()
                })

        solution = {
            'page_faults': page_faults,
            'replacement_steps': replacement_steps
        }
        return solution

    def generate_address_translation_problem(self):
        """生成地址转换问题"""
        page_size = random.choice(self.page_sizes)
        # 生成页表，最多10个页号
        page_table_size = random.randint(5, 10)
        page_table = {}
        for page in range(page_table_size):
            page_table[page] = random.randint(100, 1000)  # 帧号

        # 生成逻辑地址，确保页号在页表范围内
        logical_address = random.randint(0, page_table_size * page_size - 1)

        problem = {
            'type': 'address_translation',
            'page_size': page_size,
            'page_table': page_table,
            'logical_address': logical_address
        }

        solution = self._solve_address_translation(problem)
        return problem, solution

    @staticmethod
    def _solve_address_translation(problem):
        """解决地址转换问题"""
        page_size = problem['page_size']
        page_table = problem['page_table']
        logical_address = problem['logical_address']

        # 计算页号和页内偏移
        page_number = logical_address // page_size
        offset = logical_address % page_size

        # 检查页号是否在页表中
        if page_number not in page_table:
            return {
                'error': f"页号 {page_number} 不在页表中",
                'page_number': page_number,
                'offset': offset,
                'valid': False
            }

        # 计算物理地址
        frame_number = page_table[page_number]
        physical_address = frame_number * page_size + offset

        solution = {
            'page_number': page_number,
            'offset': offset,
            'frame_number': frame_number,
            'physical_address': physical_address,
            'valid': True
        }
        return solution

    def generate_segmentation_problem(self):
        """生成分段存储的段地址计算问题"""
        # 生成段表，最多5个段
        segment_table_size = random.randint(3, 5)
        segment_table = {}
        for segment in range(segment_table_size):
            base = random.randint(1000, 10000)
            limit = random.randint(1000, 5000)
            segment_table[segment] = (base, limit)

        # 生成逻辑地址
        segment_number = random.randint(0, segment_table_size - 1)
        # 50%的概率生成有效偏移，50%的概率生成越界偏移
        if random.random() < 0.5:
            offset = random.randint(0, segment_table[segment_number][1] - 1)
        else:
            offset = random.randint(segment_table[segment_number][1],
                                    segment_table[segment_number][1] + 1000)

        problem = {
            'type': 'segmentation',
            'segment_table': segment_table,
            'segment_number': segment_number,
            'offset': offset
        }

        solution = self._solve_segmentation(problem)
        return problem, solution

    @staticmethod
    def _solve_segmentation(problem):
        """解决分段存储的段地址计算问题"""
        segment_table = problem['segment_table']
        segment_number = problem['segment_number']
        offset = problem['offset']

        # 检查段号是否存在
        if segment_number not in segment_table:
            return {
                'error': f"段号 {segment_number} 不存在",
                'valid': False
            }

        base, limit = segment_table[segment_number]

        # 检查偏移是否越界
        if offset >= limit:
            return {
                'segment_number': segment_number,
                'offset': offset,
                'base': base,
                'limit': limit,
                'error': f"段内偏移 {offset} 越界 (段大小: {limit})",
                'valid': False
            }

        # 计算物理地址
        physical_address = base + offset

        solution = {
            'segment_number': segment_number,
            'offset': offset,
            'base': base,
            'limit': limit,
            'physical_address': physical_address,
            'valid': True
        }
        return solution

    def generate_random_problem(self):
        """随机生成一种类型的内存管理问题"""
        problem_types = [
            self.generate_page_replacement_problem,
            self.generate_address_translation_problem,
            self.generate_segmentation_problem
        ]
        generator = random.choice(problem_types)
        return generator()

    @staticmethod
    def format_problem_description(problem):
        """格式化问题描述为易读的文本"""
        if problem['type'] == 'page_replacement':
            algorithm_name = {
                'FIFO': '先进先出(FIFO)',
                'LRU': '最近最少使用(LRU)',
                'OPT': '最优置换(OPT)'
            }.get(problem['algorithm'], problem['algorithm'])

            return f"""
=== 页面置换算法问题 ===
使用{algorithm_name}算法处理页面置换。
物理块数量: {problem['frame_count']}
页面访问序列: {problem['page_sequence']}

请计算:
1. 缺页次数
2. 页面置换过程
"""

        elif problem['type'] == 'address_translation':
            page_size_kb = problem['page_size'] // 1024
            page_table_str = "\n".join(
                f"  页号 {page} -> 帧号 {frame}"
                for page, frame in problem['page_table'].items()
            )

            return f"""
=== 地址转换问题 ===
已知系统使用分页存储管理，页大小为 {page_size_kb}KB。
页表内容如下:
{page_table_str}

逻辑地址: {problem['logical_address']}

请计算:
1. 该逻辑地址对应的页号和页内偏移
2. 转换后的物理地址
"""

        elif problem['type'] == 'segmentation':
            segment_table_str = "\n".join(
                f"  段号 {segment}: 基址 = {base}, 段大小 = {limit}"
                for segment, (base, limit) in problem['segment_table'].items()
            )

            return f"""
=== 分段存储的段地址计算问题 ===
已知系统使用分段存储管理，段表内容如下:
{segment_table_str}

逻辑地址: 段号 = {problem['segment_number']}, 段内偏移 = {problem['offset']}

请计算:
1. 该逻辑地址是否有效(是否越界)
2. 如果有效，计算对应的物理地址
"""

        return "未知类型的问题"

    @staticmethod
    def format_solution_description(problem, solution):
        """格式化解决方案为易读的文本"""
        if problem['type'] == 'page_replacement':
            steps = []
            for step in solution['replacement_steps']:
                if step['replaced'] is not None:
                    steps.append(f"步骤 {step['step']}: 访问页面 {step['page']}, 置换页面 {step['replaced']}")
                else:
                    steps.append(f"步骤 {step['step']}: 访问页面 {step['page']}, 加入内存")
                steps.append(f"    内存状态: {step['frames']}")

            steps_text = "\n".join(steps)
            return f"""
=== 解决方案 ===
缺页次数: {solution['page_faults']}

置换过程:
{steps_text}
"""

        elif problem['type'] == 'address_translation':
            if 'error' in solution:
                return f"""
=== 解决方案 ===
错误: {solution['error']}
"""
            else:
                page_size = problem['page_size']
                return f"""
=== 解决方案 ===
1. 页号和页内偏移:
   页号 = {solution['page_number']}
   页内偏移 = {solution['offset']}

2. 物理地址计算:
   帧号 = {solution['frame_number']}
   物理地址 = 帧号 × 页大小 + 页内偏移
            = {solution['frame_number']} × {page_size} + {solution['offset']}
            = {solution['physical_address']}
"""

        elif problem['type'] == 'segmentation':
            if 'error' in solution:
                return f"""
=== 解决方案 ===
1. 有效性判断:
   无效。{solution['error']}

2. 物理地址:
   由于逻辑地址无效，无物理地址。
"""
            else:
                return f"""
=== 解决方案 ===
1. 有效性判断:
   有效。段内偏移 {solution['offset']} 在段大小 {solution['limit']} 范围内。

2. 物理地址计算:
   物理地址 = 基址 + 段内偏移
            = {solution['base']} + {solution['offset']}
            = {solution['physical_address']}
"""

        return "未知类型的解决方案"


if __name__ == "__main__":
    generator_ = MemoryManagementProblemGenerator()

    # # 示例1：生成随机类型的问题
    # print("=== 随机生成的内存管理问题 ===")
    # problem_, solution_ = generator_.generate_random_problem()
    # print(generator_.format_problem_description(problem_))
    # print(generator_.format_solution_description(problem_, solution_))

    # print("\n\n=== 生成特定类型的问题 ===")
    #
    # 示例2：生成页面置换问题 (LRU算法)
    print("\n--- 页面置换问题 (LRU) ---")
    page_replacement_problem, pr_solution = generator_.generate_page_replacement_problem("LRU")
    print(generator_.format_problem_description(page_replacement_problem))
    print(generator_.format_solution_description(page_replacement_problem, pr_solution))
    #
    # # 示例3：生成地址转换问题
    # print("\n--- 地址转换问题 ---")
    # address_problem, address_solution = generator_.generate_address_translation_problem()
    # print(generator_.format_problem_description(address_problem))
    # print(generator_.format_solution_description(address_problem, address_solution))
    #
    # # 示例4：生成分段存储问题
    # print("\n--- 分段存储问题 ---")
    # segmentation_problem, seg_solution = generator_.generate_segmentation_problem()
    # print(generator_.format_problem_description(segmentation_problem))
    # print(generator_.format_solution_description(segmentation_problem, seg_solution))
