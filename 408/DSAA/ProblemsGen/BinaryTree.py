import random


def generate_binary_tree_question():
    question_type = random.choice(['A', 'B'])

    if question_type == 'A':
        n1 = random.randint(0, 10)
        k = random.randint(0, 10)  # 确保n2为非负整数
        n = n1 + 1 + 2 * k
        n2 = k
        n0 = n2 + 1

        question = f"已知一棵二叉树有总节点数 n = {n}，度为1的节点数 n₁ = {n1}，求叶子节点数 n₀ 和度为2的节点数 n₂。"
        answer = f"n₀ = {n0}, n₂ = {n2}"
        explanation = \
            f"在二叉树中，总节点数n=n₀+n₁+n₂，且n₀=n₂+1。所以，代入已知值：{n}=n₀+{n1}+n₂，且n₀=n₂+1。" \
            f"解方程：从n₀=n₂+1，代入第一个方程：{n}=(n₂+1)+{n1}+n₂=2×n₂+{n1+1}，所以2×n₂={n}-{n1+1}={n-n1-1}，n₂={n2}。" \
            f"然后n₀={n2}+1={n0}。"

    else:  # 题型B
        n0 = random.randint(1, 10)
        n1 = random.randint(0, 10)
        n2 = n0 - 1
        n = n0 + n1 + n2

        question = f"已知一棵二叉树有叶子节点数 n₀ = {n0}，度为1的节点数 n₁ = {n1}，求总节点数 n 和度为2的节点数 n₂。"
        answer = f"n = {n}, n₂ = {n2}"
        explanation = \
            f"在二叉树中，n₀=n₂+1，所以n₂=n₀-1={n0}-1={n2}。总节点数n=n₀+n₁+n₂={n0}+{n1}+{n2}={n}。"

    return question, answer, explanation


if __name__ == '__main__':
    # 示例调用
    q, a, e = generate_binary_tree_question()
    print("题目:", q)
    print("答案:", a)
    print("解析:", e)
