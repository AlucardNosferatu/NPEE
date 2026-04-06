# ---------- 具体算法实现 ----------
from cop import NotApplicable, AlgorithmUnit, AlgorithmChain, NoApplicableAlgorithm


def fib_recursive(n):
    """递归法，n<=30 时可用"""
    if n < 0:
        raise NotApplicable("n 不能为负")
    if n <= 1:
        return n
    # 如果 n 太大，直接抛出 NotApplicable（尽管前置条件已检查，这里还是演示一下运行时）
    if n > 30:
        raise NotApplicable("递归法 n 太大")
    return fib_recursive(n - 1) + fib_recursive(n - 2)


def fib_iterative(n):
    """迭代法，n<=1000 时可用"""
    if n < 0:
        raise NotApplicable("n 不能为负")
    if n > 1000:
        raise NotApplicable("迭代法 n 太大")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def fib_matrix(n):
    """矩阵快速幂，通用"""
    if n < 0:
        raise NotApplicable("n 不能为负")

    # 实现矩阵快速幂
    def mat_mul(mat_a, mat_b):
        return [
            [
                mat_a[0][0] * mat_b[0][0] + mat_a[0][1] * mat_b[1][0],
                mat_a[0][0] * mat_b[0][1] + mat_a[0][1] * mat_b[1][1]
            ],
            [
                mat_a[1][0] * mat_b[0][0] + mat_a[1][1] * mat_b[1][0],
                mat_a[1][0] * mat_b[0][1] + mat_a[1][1] * mat_b[1][1]
            ]
        ]

    def mat_pow(mat, k):
        result = [[1, 0], [0, 1]]
        while k:
            if k & 1:
                result = mat_mul(result, mat)
            mat = mat_mul(mat, mat)
            k >>= 1
        return result

    if n == 0:
        return 0
    mat_fib = [[1, 1], [1, 0]]
    mat_pow_n = mat_pow(mat_fib, n - 1)
    return mat_pow_n[0][0]


# 前置条件函数
def pre_recursive(n):
    return 0 <= n <= 30


def pre_iterative(n):
    return 0 <= n <= 1000


def pre_matrix(n):
    return n >= 0  # 矩阵法适用任何非负整数


# 后置条件：结果必须非负（总是成立，但为了演示）
def post_non_neg(data, result):
    _ = data
    return result >= 0


# 组装算法链
algorithms = [
    AlgorithmUnit(fib_recursive, pre_condition=pre_recursive, post_condition=post_non_neg, name="递归"),
    AlgorithmUnit(fib_iterative, pre_condition=pre_iterative, post_condition=post_non_neg, name="迭代"),
    AlgorithmUnit(fib_matrix, pre_condition=pre_matrix, post_condition=post_non_neg, name="矩阵")
]

chain = AlgorithmChain(algorithms)

# 测试不同输入
test_inputs = [10, 35, 1000, 2000, -5]

for n_ in test_inputs:
    print(f"\n=== 测试 n={n_} ===")
    try:
        result_ = chain.run(n_)
        print(f"最终结果: fib({n_}) = {result_}")
    except NoApplicableAlgorithm as e:
        print(f"错误: {e}")
    except Exception as e:
        print(f"未处理异常: {e}")
