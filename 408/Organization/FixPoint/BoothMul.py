import random


def to_twos_complement(n, bits):
    if n >= 0:
        return bin(n)[2:].zfill(bits)
    else:
        return bin((1 << bits) + n)[2:]


def from_twos_complement(s):
    if s[0] == '1':
        return -int(''.join('1' if c == '0' else '0' for c in s[1:]), 2) - 1
    else:
        return int(s, 2)


def generate_multiplication():
    bits = 4
    x = random.randint(-7, 7)
    y = random.randint(-7, 7)
    x_tc = to_twos_complement(x, bits)
    y_tc = to_twos_complement(y, bits)
    steps = []

    # Booth算法初始化
    A = '0' * bits
    Q = y_tc
    Q_1 = '0'
    M = x_tc
    steps.append(f"初始化：A={A}, Q={Q}, Q₋₁={Q_1}, M={M}")

    for i in range(bits):
        q0 = Q[-1]
        if (q0, Q_1) == ('0', '1'):
            # 加M
            A = bin(int(A, 2) + int(M, 2))[2:].zfill(bits)
            if len(A) > bits: A = A[-bits:]
            steps.append(f"步骤{i + 1}: Q0Q-1=01 ➔ 加M → A={A}")
        elif (q0, Q_1) == ('1', '0'):
            # 减M
            A = bin(int(A, 2) + int(to_twos_complement(-x, bits), 2))[2:].zfill(bits)
            if len(A) > bits: A = A[-bits:]
            steps.append(f"步骤{i + 1}: Q0Q-1=10 ➔ 减M → A={A}")
        else:
            steps.append(f"步骤{i + 1}: Q0Q-1={q0}{Q_1} ➔ 无操作")

        # 算术右移
        Q_1 = Q[-1]
        Q = A[-1] + Q[:-1]
        A = A[0] + A[:-1]
        steps.append(f"右移后：A={A}, Q={Q}, Q₋₁={Q_1}")

    result = A + Q
    return {
        "type": "乘法",
        "x": x,
        "y": y,
        "steps": steps,
        "result": from_twos_complement(result)
    }


problem = generate_multiplication()

# 输出题目
print(f"题目：进行定点数{problem['type']}运算")
print(f"计算 {problem['x']} × {problem['y']} 使用Booth算法")

# 输出答案步骤
print("\n解答步骤：")
for step in problem['steps']:
    print(f"→ {step}")

print(f"最终结果：{problem['result']}")
