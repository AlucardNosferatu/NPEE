import random
from Calculation import (
    catalan_number,
    st_insert_and_delete,
    cq_empty_or_full
)

class ProblemGenerator:
    def __init__(self):
        self.problem_types = {
            1: self.generate_stack_order_problem,
            2: self.generate_sequence_table_problem,
            3: self.generate_circular_queue_problem
        }

    def generate_stack_order_problem(self):
        """生成栈的出栈顺序数量问题及解析"""
        n = random.randint(3, 10)
        answer = int(catalan_number(n))
        question = f"{n} 个不同元素依次进栈，可能的出栈顺序有多少种？"
        explanation = (
            f"解析：n个不同元素的出栈顺序总数由卡特兰数计算，公式为 C(2n, n)/(n+1)。\n"
            f"其中组合数 C(2n, n) = (2n)!/(n!·n!)，代入n={n}得：\n"
            f"C(2×{n}, {n}) = {int(catalan_number(n) * (n+1))}，因此结果为 {int(catalan_number(n) * (n+1))}/{n+1} = {answer}"
        )
        return {
            "type": "栈的出栈顺序数量",
            "question": question,
            "answer": answer,
            "explanation": explanation
        }

    def generate_sequence_table_problem(self):
        """生成顺序表增删操作移动元素问题及解析"""
        length = random.randint(100, 1000)
        n = random.randint(1, length)
        answer = st_insert_and_delete(length, n)
        question = f"对长度为 {length} 的顺序表，操作第 {n} 个元素（增删）时，需要移动多少个元素？"
        explanation = (
            f"解析：顺序表采用连续存储，增删第n个元素时，需移动其后续所有元素。\n"
            f"后续元素数量为总长度 - 位置索引（从1开始），即 {length} - {n} = {answer}"
        )
        return {
            "type": "顺序表元素移动",
            "question": question,
            "answer": answer,
            "explanation": explanation
        }

    def generate_circular_queue_problem(self):
        """生成循环队列状态判断问题及解析"""
        max_size = random.randint(5, 20)
        front_pos = random.randint(0, max_size - 1)
        rear_pos = random.randint(0, max_size - 1)
        last_op = random.choice(['insert', 'delete', None])
        
        # 确保生成有效状态（避免矛盾的last_op）
        if front_pos == rear_pos and last_op is not None:
            if last_op == 'insert':
                # 插入后满队列：(rear+1)%max_size == front
                rear_pos = (front_pos - 1) % max_size
            else:
                # 删除后空队列：保持front=rear
                pass
        
        answer = cq_empty_or_full(max_size, front_pos, rear_pos, last_op)
        status = "空队列" if answer == 0 else "满队列" if answer == max_size else f"包含 {answer} 个元素"
        
        question = (
            f"循环队列最大容量为 {max_size}，队头位置 front={front_pos}，队尾位置 rear={rear_pos}，\n"
            f"最后一次操作为：{'无' if last_op is None else '插入' if last_op == 'insert' else '删除'}，\n"
            f"请判断队列当前状态（空/满/元素数量）？"
        )
        explanation = (
            f"解析：循环队列状态判断逻辑如下：\n"
            f"1. 当 front == rear 时：\n"
            f"   - 若最后操作为插入（insert）→ 满队列（{max_size}个元素）\n"
            f"   - 若最后操作为删除（delete）→ 空队列（0个元素）\n"
            f"2. 其他情况：元素数量 = (rear + max_size - front) % max_size\n"
            f"当前计算：({rear_pos} + {max_size} - {front_pos}) % {max_size} = {answer} → {status}"
        )
        return {
            "type": "循环队列状态判断",
            "question": question,
            "answer": status if answer in (0, max_size) else answer,
            "explanation": explanation
        }

    def generate_random_problem(self):
        """随机生成一种类型的题目"""
        problem_type = random.choice(list(self.problem_types.keys()))
        return self.problem_types[problem_type]()

    def run(self):
        """交互式生成题目并展示答案和解析"""
        while True:
            print("\n===== 数据结构练习题生成器 =====")
            print("1. 栈的出栈顺序数量")
            print("2. 顺序表元素移动")
            print("3. 循环队列状态判断")
            print("4. 随机生成一题")
            print("0. 退出")
            
            choice = input("请选择题目类型（输入数字）：")
            if choice == '0':
                print("退出程序，再见！")
                break
            if choice not in ['1', '2', '3', '4']:
                print("无效输入，请重新选择")
                continue
            
            problem = self.problem_types[int(choice)]() if choice != '4' else self.generate_random_problem()
            
            print(f"\n【题目类型】：{problem['type']}")
            print(f"【题目】：{problem['question']}")
            
            input("\n按回车查看答案...")
            print(f"【答案】：{problem['answer']}")
            
            input("\n按回车查看解析...")
            print(f"【解析】：{problem['explanation']}\n")


if __name__ == "__main__":
    generator = ProblemGenerator()
    generator.run()
