import fractions
import random

import numpy as np


def generate_orthogonalization_problem():
    """
    生成三个线性无关向量
    """
    while True:
        # 随机生成整数向量
        v1 = np.array([random.randint(-3, 3) for _ in range(3)])
        v2 = np.array([random.randint(-3, 3) for _ in range(3)])
        v3 = np.array([random.randint(-3, 3) for _ in range(3)])

        # 检查是否线性无关
        matrix = np.array([v1, v2, v3])
        if np.linalg.matrix_rank(matrix) == 3:
            break

    return v1, v2, v3


def gram_schmidt(v1, v2, v3):
    """
    对三个向量进行施密特正交化
    """
    u1 = v1.astype(float)

    # u2 = v2 - proj_u1(v2)
    proj_u1_v2 = (np.dot(v2, u1) / np.dot(u1, u1)) * u1
    u2 = v2.astype(float) - proj_u1_v2

    # u3 = v3 - proj_u1(v3) - proj_u2(v3)
    proj_u1_v3 = (np.dot(v3, u1) / np.dot(u1, u1)) * u1
    proj_u2_v3 = (np.dot(v3, u2) / np.dot(u2, u2)) * u2
    u3 = v3.astype(float) - proj_u1_v3 - proj_u2_v3

    return u1, u2, u3


def normalize_vector(v):
    """
    单位化向量
    """
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def vector_to_str(v):
    """
    将向量转换为字符串
    """
    return f"[{', '.join(str(x) for x in v)}]"


def fraction_str(x):
    """
    将数转换为分数形式的字符串
    """
    frac = fractions.Fraction(x).limit_denominator()
    if frac.denominator == 1:
        return str(frac.numerator)
    else:
        return f"{frac.numerator}/{frac.denominator}"


def vector_to_fraction_str(v):
    """
    将向量转换为分数形式的字符串
    """
    return f"[{', '.join(fraction_str(x) for x in v)}]"


def interactive_gram_schmidt():
    """
    交互式施密特正交化练习
    """
    print("=" * 60)
    print("施密特正交化习题生成器")
    print("=" * 60)

    # 生成问题
    v1, v2, v3 = generate_orthogonalization_problem()
    print(f"\n给定三个线性无关向量：")
    print(f"v1 = {vector_to_str(v1)}")
    print(f"v2 = {vector_to_str(v2)}")
    print(f"v3 = {vector_to_str(v3)}")

    print(f"\n请使用施密特正交化方法构造一组标准正交基。")
    input("\n按回车键查看解答步骤...")

    # 显示解答步骤
    print("\n" + "=" * 40)
    print("解答步骤")
    print("=" * 40)

    # 步骤1：正交化过程
    print("\n步骤1：正交化过程")
    print("-" * 30)

    # u1 = v1
    u1 = v1.astype(float)
    print(f"1. 令 u1 = v1 = {vector_to_str(v1)}")

    # u2 = v2 - proj_u1(v2)
    dot_v2_u1 = np.dot(v2, u1)
    dot_u1_u1 = np.dot(u1, u1)
    proj_coeff = dot_v2_u1 / dot_u1_u1
    proj_u1_v2 = proj_coeff * u1
    u2 = v2.astype(float) - proj_u1_v2

    print(f"\n2. 计算 u2 = v2 - proj_u1(v2)")
    print(f"   ⟨v2, u1⟩ = {dot_v2_u1}")
    print(f"   ⟨u1, u1⟩ = {dot_u1_u1}")
    print(f"   投影系数 = ⟨v2, u1⟩/⟨u1, u1⟩ = {fraction_str(proj_coeff)}")
    print(f"   proj_u1(v2) = {fraction_str(proj_coeff)} × {vector_to_str(u1)}")
    print(f"               = {vector_to_fraction_str(proj_u1_v2)}")
    print(f"   u2 = v2 - proj_u1(v2)")
    print(f"      = {vector_to_str(v2)} - {vector_to_fraction_str(proj_u1_v2)}")
    print(f"      = {vector_to_fraction_str(u2)}")

    # u3 = v3 - proj_u1(v3) - proj_u2(v3)
    dot_v3_u1 = np.dot(v3, u1)
    dot_v3_u2 = np.dot(v3, u2)
    dot_u2_u2 = np.dot(u2, u2)
    proj_coeff1 = dot_v3_u1 / dot_u1_u1
    proj_coeff2 = dot_v3_u2 / dot_u2_u2
    proj_u1_v3 = proj_coeff1 * u1
    proj_u2_v3 = proj_coeff2 * u2
    u3 = v3.astype(float) - proj_u1_v3 - proj_u2_v3

    print(f"\n3. 计算 u3 = v3 - proj_u1(v3) - proj_u2(v3)")
    print(f"   ⟨v3, u1⟩ = {dot_v3_u1}, ⟨v3, u2⟩ = {dot_v3_u2}")
    print(f"   ⟨u2, u2⟩ = {dot_u2_u2}")
    print(f"   投影系数1 = ⟨v3, u1⟩/⟨u1, u1⟩ = {fraction_str(proj_coeff1)}")
    print(f"   投影系数2 = ⟨v3, u2⟩/⟨u2, u2⟩ = {fraction_str(proj_coeff2)}")
    print(f"   proj_u1(v3) = {fraction_str(proj_coeff1)} × {vector_to_str(u1)}")
    print(f"                = {vector_to_fraction_str(proj_u1_v3)}")
    print(f"   proj_u2(v3) = {fraction_str(proj_coeff2)} × {vector_to_fraction_str(u2)}")
    print(f"                = {vector_to_fraction_str(proj_u2_v3)}")
    print(f"   u3 = v3 - proj_u1(v3) - proj_u2(v3)")
    print(f"      = {vector_to_str(v3)} - {vector_to_fraction_str(proj_u1_v3)} - {vector_to_fraction_str(proj_u2_v3)}")
    print(f"      = {vector_to_fraction_str(u3)}")

    input("\n按回车键继续查看单位化过程...")

    # 步骤2：单位化过程
    print("\n步骤2：单位化过程")
    print("-" * 30)

    # 单位化
    norm_u1 = np.linalg.norm(u1)
    norm_u2 = np.linalg.norm(u2)
    norm_u3 = np.linalg.norm(u3)

    e1 = normalize_vector(u1)
    e2 = normalize_vector(u2)
    e3 = normalize_vector(u3)

    print(f"1. 计算 e1 = u1 / ||u1||")
    print(f"   ||u1|| = √{dot_u1_u1} = {norm_u1:.4f}")
    print(f"   e1 = {vector_to_fraction_str(u1)} / {norm_u1:.4f}")
    print(f"      = [{', '.join(f'{x:.4f}' for x in e1)}]")

    print(f"\n2. 计算 e2 = u2 / ||u2||")
    print(f"   ||u2|| = √{dot_u2_u2} = {norm_u2:.4f}")
    print(f"   e2 = {vector_to_fraction_str(u2)} / {norm_u2:.4f}")
    print(f"      = [{', '.join(f'{x:.4f}' for x in e2)}]")

    print(f"\n3. 计算 e3 = u3 / ||u3||")
    print(f"   ||u3|| = √{np.dot(u3, u3)} = {norm_u3:.4f}")
    print(f"   e3 = {vector_to_fraction_str(u3)} / {norm_u3:.4f}")
    print(f"      = [{', '.join(f'{x:.4f}' for x in e3)}]")

    # 最终结果
    print("\n" + "=" * 40)
    print("最终结果")
    print("=" * 40)
    print(f"通过施密特正交化得到的一组标准正交基为：")
    print(f"e1 = [{', '.join(f'{x:.4f}' for x in e1)}]")
    print(f"e2 = [{', '.join(f'{x:.4f}' for x in e2)}]")
    print(f"e3 = [{', '.join(f'{x:.4f}' for x in e3)}]")

    # 验证结果
    print(f"\n验证正交性：")
    print(f"⟨e1, e2⟩ = {np.dot(e1, e2):.6f} (应为0)")
    print(f"⟨e1, e3⟩ = {np.dot(e1, e3):.6f} (应为0)")
    print(f"⟨e2, e3⟩ = {np.dot(e2, e3):.6f} (应为0)")
    print(f"\n验证单位长度：")
    print(f"||e1|| = {np.linalg.norm(e1):.6f} (应为1)")
    print(f"||e2|| = {np.linalg.norm(e2):.6f} (应为1)")
    print(f"||e3|| = {np.linalg.norm(e3):.6f} (应为1)")


def main():
    """
    主函数
    """
    while True:
        interactive_gram_schmidt()

        print("\n" + "=" * 60)
        continue_choice = input("是否继续生成新题目？(y/n): ").strip().lower()
        if continue_choice != 'y':
            print("谢谢使用！")
            break
        print()


if __name__ == "__main__":
    main()
