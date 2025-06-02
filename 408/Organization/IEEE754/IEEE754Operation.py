import random


def generate_float():
    """生成符合条件的随机浮点数"""
    # 生成整数部分 (-500 到 500 之间)
    integer_part = random.randint(-500, 500)

    # 生成小数部分 (最多3个2的负幂之和，指数范围从-1到-4)
    exponents = list(range(-1, -5, -1))  # [-1, -2, -3, -4]
    random.shuffle(exponents)
    # 随机选择1到3个不同的指数
    num_exponents = random.randint(1, 3)
    selected_exponents = exponents[:num_exponents]

    # 计算小数部分
    fractional_part = sum(2 ** exp for exp in selected_exponents)

    # 合并整数和小数部分
    return integer_part + fractional_part


