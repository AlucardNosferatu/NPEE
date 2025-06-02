import random

from IEEE754Operation import generate_float, parse_ieee754, compute_sign_and_magnitude, normalize_result, \
    format_ieee754, float_to_ieee754, align_exponents


def generate_question():
    # 随机生成操作数和运算符
    a = generate_float()
    b = generate_float()
    operator = random.choice(["+", "-"])
    a_ieee754 = float_to_ieee754(a)
    b_ieee754 = float_to_ieee754(b)
    # 获取IEEE754表示
    sign1, E1, M1 = parse_ieee754(a_ieee754)
    sign2, E2, M2 = parse_ieee754(b_ieee754)

    # 执行运算步骤
    # ----------对阶阶段----------
    delta_E = E1 - E2
    # 对阶
    E_aligned, M1_aligned, M2_aligned = align_exponents(E1, E2, M1, M2)

    # 尾数加减
    sign_result, M_sum_abs = compute_sign_and_magnitude(
        sign1, sign2, M1_aligned, M2_aligned, operator
    )

    # 规格化处理
    M_normalized, E_normalized = normalize_result(M_sum_abs, E_aligned)

    # 构造题目与答案
    question = f"计算 {a} {operator} {b} 的IEEE754运算过程，要求：\n" \
               "1) 写出对阶时的阶差及调整后的尾数\n" \
               "2) 尾数加减结果\n" \
               "3) 规格化后的指数和尾数\n" \
               "4) 最终IEEE754二进制表示"

    answer = f"【解析】\n" \
             f"原始数1：符号位={sign1}，阶码={E1}，尾数={M1}\n" \
             f"原始数2：符号位={sign2}，阶码={E2}，尾数={M2}\n" \
             f"1) 阶差ΔE={delta_E}，调整后尾数：\n" \
             f"   num1尾数={M1}\n" \
             f"   num2尾数={M2}\n" \
             f"   共同阶码={E_aligned}\n" \
             f"2) 尾数运算结果：符号={sign_result}，绝对值={M_sum_abs}\n" \
             f"3) 规格化处理：尾数={M_normalized}，阶码={E_normalized}\n" \
             f"4) 最终结果：{format_ieee754(sign_result, E_normalized, M_normalized)}"

    return question, answer


# 示例输出
q, a = generate_question()
print("题目：\n", q)
print("\n答案：\n", a)
