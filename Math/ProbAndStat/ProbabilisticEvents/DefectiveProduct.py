import sympy
import math


def comb(n, m):
    # 直接使用math里的阶乘函数计算组合数
    return math.factorial(n) // (math.factorial(n - m) * math.factorial(m))


def perm(n, m):
    # 直接使用math里的阶乘函数计算排列数
    return math.factorial(n) // math.factorial(n - m)


class ABatchOfProduct:
    DPCount = 0
    NDPCount = 0

    def __init__(self, dp_count, ndp_count):
        self.DPCount = dp_count
        self.NDPCount = ndp_count

    def total_product_count(self):
        return self.DPCount + self.NDPCount

    def one_time_single(self):
        return sympy.Rational(self.DPCount, self.DPCount + self.NDPCount)

    def one_time_multiple(self, exp_times, dp_times):
        numerator = comb(self.DPCount, dp_times) * comb(self.NDPCount, exp_times - dp_times)
        denominator = comb(self.total_product_count(), exp_times)
        return sympy.Rational(numerator, denominator)

    def sequential_multiple_with_replacement(self, exp_times, dp_times):
        arrange = comb(exp_times, dp_times)
        dp_prob = self.one_time_single() ** dp_times
        ndp_prob = (1 - self.one_time_single()) ** (exp_times - dp_times)
        return arrange * dp_prob * ndp_prob

    def sequential_multiple_without_replacement(self, exp_times, dp_times):
        numerator = perm(self.DPCount, dp_times) * perm(self.NDPCount, exp_times - dp_times)
        denominator = perm(self.total_product_count(), exp_times)
        arrange = comb(exp_times, dp_times)
        return sympy.Rational(numerator, denominator) * arrange


if __name__ is '__main__':
    abop = ABatchOfProduct(40, 60)
    p1 = abop.one_time_multiple(3, 1)
    p2 = abop.sequential_multiple_with_replacement(3, 1)
    p3 = abop.sequential_multiple_without_replacement(3, 1)
    print(p1, p2, p3)
