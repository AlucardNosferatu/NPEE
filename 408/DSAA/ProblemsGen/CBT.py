import math
import random


def generate_complete_binary_tree_question():
    question_type = random.choice(['A', 'B', 'C'])

    if question_type == 'A':  # 深度计算
        subtype = random.choice(['nodes_to_depth', 'depth_to_nodes'])

        if subtype == 'nodes_to_depth':
            n = random.randint(1, 100)
            h = math.floor(math.log2(n)) + 1

            question = f"一棵完全二叉树有 {n} 个节点，求该树的深度。"
            answer = f"深度为 {h}"
            explanation = f"对于有n个节点的完全二叉树，深度h = ⌊log₂n⌋ + 1。计算得：⌊log₂{n}⌋ + 1 = {h}。"

        else:  # depth_to_nodes
            h = random.randint(2, 7)
            min_nodes = 2 ** (h - 1)
            max_nodes = 2 ** h - 1

            question = f"深度为 {h} 的完全二叉树，节点数范围是多少？"
            answer = f"最少 {min_nodes} 个节点，最多 {max_nodes} 个节点"
            explanation = f"深度为h的完全二叉树：最少节点数 = 2^(h-1) = {min_nodes}，最多节点数 = 2^h - 1 = {max_nodes}。"

    elif question_type == 'B':  # 父子节点关系
        i = random.randint(2, 50)  # 避免根节点，因为根节点没有父节点
        parent = i // 2
        left_child = 2 * i
        right_child = 2 * i + 1

        question = f"在完全二叉树中（根节点下标为1），节点 {i} 的父节点、左孩子和右孩子的下标分别是多少？"
        answer = f"父节点：{parent}，左孩子：{left_child}，右孩子：{right_child}"
        explanation = f"完全二叉树中：" \
                      f"父节点 = ⌊i/2⌋ = ⌊{i}/2⌋ = {parent}，" \
                      f"左孩子 = 2×i = 2×{i} = {left_child}，" \
                      f"右孩子 = 2×i+1 = 2×{i}+1 = {right_child}。"

    else:  # 题型C: 层级计算
        i = random.randint(1, 100)
        level = math.floor(math.log2(i)) + 1

        question = f"在完全二叉树中（根节点下标为1），节点 {i} 位于第几层？"
        answer = f"第 {level} 层"
        explanation = f"节点i所在的层级 = ⌊log₂i⌋ + 1 = ⌊log₂{i}⌋ + 1 = {level}。"

    return question, answer, explanation


# 示例使用
if __name__ == "__main__":
    for i_ in range(3):
        print(f"\n--- 示例 {i_ + 1} ---")
        q, a, e = generate_complete_binary_tree_question()
        print("题目:", q)
        print("答案:", a)
        print("解析:", e)
