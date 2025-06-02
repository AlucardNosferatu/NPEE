def decimal_to_binary(n, bits=8):
    """将十进制数转换为指定位数的二进制字符串，考虑补码"""
    if n < 0:
        n = (1 << bits) + n  # 转换为补码
    binary = bin(n)[2:].zfill(bits)
    return binary


def binary_to_decimal(binary, bits=8):
    """将二进制字符串转换为十进制数，考虑补码"""
    if binary[0] == '1':
        return int(binary, 2) - (1 << bits)
    return int(binary, 2)


def binary_division_dividend(dividend, divisor, bits=8):
    """模拟定点整数二进制恢复余数法的计算过程"""
    if divisor == 0:
        raise ValueError("除数不能为 0")

    # 取绝对值进行计算
    dividend_abs = abs(dividend)
    divisor_abs = abs(divisor)

    # 初始化
    Q = dividend_abs  # 商的绝对值
    M = divisor_abs  # 除数的绝对值
    A = 0  # 累加器

    # 计算过程记录
    steps = []

    # 恢复余数法
    for i in range(bits):
        # 1. A和Q左移一位
        A = (A << 1) | ((Q >> (bits - 1)) & 1)
        Q = (Q << 1) & ((1 << bits) - 1)

        # 记录移位后的状态
        step_info = {
            'step': i + 1,
            'operation': 'Shift left',
            'A_before': decimal_to_binary(A >> 1, bits),
            'Q_before': decimal_to_binary(Q >> 1, bits),
            'A_after': decimal_to_binary(A, bits),
            'Q_after': decimal_to_binary(Q, bits),
            'subtract_M': False,
            'restore': False,
            'Q_bit': 0
        }
        steps.append(step_info.copy())

        # 2. A减去除数M
        A_temp = A - M
        step_info['operation'] = 'Subtract M'
        step_info['A_after_subtract'] = decimal_to_binary(A_temp, bits)
        step_info['subtract_M'] = True

        # 3. 判断符号
        if A_temp >= 0:
            # 余数为正，商上1
            A = A_temp
            Q |= 1
            step_info['Q_bit'] = 1
            step_info['A_final'] = decimal_to_binary(A, bits)
            step_info['Q_final'] = decimal_to_binary(Q, bits)
        else:
            # 余数为负，恢复余数（加回M），商上0
            A = A_temp + M
            step_info['restore'] = True
            step_info['A_after_restore'] = decimal_to_binary(A, bits)
            step_info['A_final'] = decimal_to_binary(A, bits)
            step_info['Q_final'] = decimal_to_binary(Q, bits)

        steps.append(step_info)

    # 确定商和余数的符号
    quotient_sign = -1 if (dividend < 0) ^ (divisor < 0) else 1
    remainder_sign = -1 if dividend < 0 else 1

    quotient = Q if quotient_sign > 0 else ((1 << bits) - Q)
    remainder = A if remainder_sign > 0 else ((1 << bits) - A)

    return {
        'dividend': dividend,
        'divisor': divisor,
        'dividend_binary': decimal_to_binary(dividend, bits),
        'divisor_binary': decimal_to_binary(divisor, bits),
        'quotient': quotient,
        'remainder': remainder,
        'quotient_binary': decimal_to_binary(quotient, bits),
        'remainder_binary': decimal_to_binary(remainder, bits),
        'steps': steps
    }


def generate_question():
    """生成随机的定点整数除法题目"""
    bits = 8  # 8位定点整数
    dividend = 0
    # 随机生成被除数和除数
    while True:
        divisor = random.randint(-(1 << (bits - 1)) + 1, (1 << (bits - 1)) - 1)
        if divisor == 0:
            continue
        dividend = random.randint(-(1 << (bits - 1)), (1 << (bits - 1)) - 1)
        if abs(dividend) >= abs(divisor):
            break

    return dividend, divisor, bits


def format_question(dividend, divisor, bits):
    """格式化题目文本"""
    question = f"""考研408定点整数二进制除法题目：
使用恢复余数法计算以下定点整数的二进制除法：
  被除数：{dividend} (二进制: {decimal_to_binary(dividend, bits)})
  除数：{divisor} (二进制: {decimal_to_binary(divisor, bits)})

要求：
1. 写出恢复余数法的详细计算过程
2. 给出每一步的操作（左移、减除数、恢复余数）
3. 最终商和余数的二进制表示和十进制值
"""
    return question


def format_answer(result):
    """格式化答案文本"""
    answer = f"""答案：

计算 {result['dividend']} ÷ {result['divisor']} 的恢复余数法过程：

1. 初始值：
   被除数: {result['dividend']} (二进制: {result['dividend_binary']})
   除数: {result['divisor']} (二进制: {result['divisor_binary']})

2. 计算过程：
"""
    # 添加计算步骤
    for i, step in enumerate(result['steps']):
        if step['operation'] == 'Shift left':
            answer += f"\n步骤 {step['step']}: 左移\n"
            answer += f"  A: {step['A_before']} ({binary_to_decimal(step['A_before'])}) → {step['A_after']} ({binary_to_decimal(step['A_after'])})\n"
            answer += f"  Q: {step['Q_before']} ({binary_to_decimal(step['Q_before'])}) → {step['Q_after']} ({binary_to_decimal(step['Q_after'])})\n"
        elif step['operation'] == 'Subtract M':
            answer += f"步骤 {step['step']}: 减去除数 M ({result['divisor_binary']} {result['divisor']})\n"
            answer += f"  A: {step['A_after']} ({binary_to_decimal(step['A_after'])}) - M = {step['A_after_subtract']} ({binary_to_decimal(step['A_after_subtract'])})\n"
            if step['restore']:
                answer += f"  余数为负，恢复余数: {step['A_after_subtract']} ({binary_to_decimal(step['A_after_subtract'])}) + M = {step['A_after_restore']} ({binary_to_decimal(step['A_after_restore'])})\n"
                answer += f"  商位上0\n"
            else:
                answer += f"  余数为正，商位上1\n"
            answer += f"  最终 A: {step['A_final']} ({binary_to_decimal(step['A_final'])})\n"
            answer += f"  最终 Q: {step['Q_final']} ({binary_to_decimal(step['Q_final'])})\n"

    # 添加最终结果
    answer += f"""
3. 最终结果：
   商: {result['quotient']} (二进制: {result['quotient_binary']})
   余数: {result['remainder']} (二进制: {result['remainder_binary']})

4. 验证：
   {result['divisor']} × {result['quotient']} + {result['remainder']} = {result['divisor'] * result['quotient'] + result['remainder']}
   与被除数 {result['dividend']} 一致。
"""
    return answer


import random


def main(dividend=None, divisor=None, bits=8):
    """主函数：生成题目和答案并打印"""
    try:
        # 生成题目
        if dividend is None or divisor is None or bits is None:
            dividend, divisor, bits = generate_question()

        # 计算结果
        result = binary_division_dividend(dividend, divisor, bits)

        # 格式化题目和答案
        question = format_question(dividend, divisor, bits)
        answer = format_answer(result)

        # 打印题目和答案
        print("=" * 50)
        print("题目:")
        print(question)
        print("=" * 50)
        print("答案:")
        print(answer)
        print("=" * 50)
    except ValueError as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    # main(dividend=127, divisor=8)
    main()
