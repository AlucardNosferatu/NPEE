import numpy
import tqdm
import sympy
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')


def trunc(values, decs=0):
    return numpy.trunc(values * 10 ** decs) / (10 ** decs)


class DiscreteRandomVar:
    dist_laws = None
    dist_funcs = None
    regions = None
    rv_type = None
    cache = None

    def __init__(self, laws=None, seg_p=None, funcs=None):
        if type(seg_p[0]) in [int, float]:
            self.rv_type = 'finite'
            self.regions = []
            for i in range(0, len(seg_p)):
                point = seg_p[i]
                if i == 0:
                    region = [-sympy.oo, point]
                else:
                    region = [seg_p[i - 1], point]
                self.regions.append(region)
            self.regions.append([seg_p[-1], sympy.oo])
        elif hasattr(seg_p[0], 'free_symbols') and len(seg_p[0].free_symbols) > 0:
            self.rv_type = 'infinite'
            self.regions = seg_p[0]
            self.cache = []
        else:
            raise TypeError('seg_points must be specified!')
        if laws is not None:
            self.dist_laws = laws
            self.dist_funcs = self.get_funcs_from_laws()
        else:
            assert funcs is not None
            self.dist_funcs = funcs
            self.dist_laws = self.get_laws_from_funcs()

    def get_prob(self, x, use_pmf=False):
        # P{X<=x}
        p = 0
        if self.rv_type == 'finite':
            for i in range(0, len(self.regions) - 1):
                region = self.regions[i]
                if region[0] < x:
                    if use_pmf:
                        p += self.dist_laws[i]
                    if x <= region[1]:
                        if not use_pmf:
                            p = self.dist_funcs[i]
                        break
            if self.regions[-1][0] <= x < self.regions[-1][1]:
                p = 1
        else:
            n0 = 0
            n = list(self.regions.free_symbols)[0]
            if len(self.cache) == 0:
                self.cache.append(0.0)
            while self.regions.evalf(subs={n: n0}) <= sympy.sympify(x).evalf():
                if use_pmf:
                    if len(self.cache) >= n0 + 1:
                        pass
                    else:
                        self.cache.append(
                            self.cache[-1] + self.dist_laws.evalf(subs={n: n0}))
                    p = self.cache[n0]
                    if self.cache[n0] >= 1:
                        self.cache[n0] = 1
                        p = 1
                        break
                # endregion
                n0 += 1
            if not use_pmf:
                p = self.dist_funcs.evalf(subs={n: n0 - 1})
        if type(p) is not float:
            p = float(p)
        p = trunc(p, 8)
        return p

    def get_funcs_from_laws(self):
        if self.rv_type == 'finite':
            temp = 0
            dist_funcs = []
            for i in range(0, len(self.dist_laws)):
                temp += self.dist_laws[i]
                dist_funcs.append(temp)
            return dist_funcs
        else:
            n = list(self.dist_laws.free_symbols)[0]
            f = sympy.summation(self.dist_laws, (n, 1, n))
            f = f.simplify()
            return f

    def get_laws_from_funcs(self):
        if self.rv_type == 'finite':
            dist_laws = []
            for i in range(0, len(self.dist_funcs)):
                index = len(self.dist_funcs) - i - 1
                if index == 0:
                    dist_laws.insert(0, self.dist_funcs[index])
                else:
                    dist_laws.insert(
                        0,
                        self.dist_funcs[index] - self.dist_funcs[index - 1]
                    )
            return dist_laws
        else:
            n = list(self.dist_funcs.free_symbols)[0]
            laws = sympy.difference_delta(self.dist_funcs, n, 1)
            laws = laws.subs(n, n - 1).simplify()
            return laws


class PoissonDist(DiscreteRandomVar):
    def __init__(self, _lambda):
        assert _lambda > 0
        k_var = sympy.Symbol('k')
        laws_func = (_lambda ** k_var) / (sympy.factorial(k_var) * sympy.exp(_lambda))
        super().__init__(
            laws=laws_func,
            seg_p=[k_var]
        )
        self.cache.append(self.dist_laws.evalf(subs={k_var: 0}))

    def get_prob(self, x, use_pmf=True):
        if not use_pmf:
            use_pmf = True
            print('Poisson Dist Prob can only be calculated using PMF.')
        return super().get_prob(x=x, use_pmf=use_pmf)


class GeometricDist(DiscreteRandomVar):
    def __init__(self, p):
        assert 0 <= p <= 1
        k_var = sympy.Symbol('k')
        laws_func = p * ((1 - p) ** (k_var - 1))
        super().__init__(
            laws=laws_func,
            seg_p=[k_var]
        )

    def get_prob(self, x, use_pmf=False, include_success=True):
        if not include_success:
            x += 1
        return super().get_prob(x=x, use_pmf=use_pmf)


class HyperGeometricDist(DiscreteRandomVar):
    def __init__(self, total_count, defect_count, n_exp_times):
        assert total_count >= defect_count
        assert total_count >= n_exp_times
        laws_list = []
        k_var = sympy.Symbol('k')
        laws_func = sympy.binomial(
            defect_count,
            k_var
        ) * sympy.binomial(
            total_count - defect_count,
            n_exp_times - k_var
        ) / sympy.binomial(
            total_count,
            n_exp_times
        )
        seg_p = list(range(0, n_exp_times + 1))
        for i in seg_p:
            laws_list.append(laws_func.evalf(subs={k_var: i}))
        super().__init__(
            laws=laws_list,
            seg_p=seg_p
        )


class BinomialDist(DiscreteRandomVar):
    n = None
    p = None

    def __init__(self, n_exp_times, p):
        self.n = n_exp_times
        self.p = p
        assert 0 <= p <= 1
        laws_list = []
        k_var = sympy.Symbol('k')
        laws_func = sympy.binomial(
            n_exp_times,
            k_var
        ) * (p ** k_var) * ((1 - p) ** (n_exp_times - k_var))
        seg_p = list(range(0, n_exp_times + 1))
        for i in seg_p:
            laws_list.append(laws_func.evalf(subs={k_var: i}))
        super().__init__(
            laws=laws_list,
            seg_p=seg_p
        )

    def poisson_theorem(self):
        return PoissonDist(self.n * self.p)


class ZeroOneDist(BinomialDist):
    def __init__(self, p):
        super().__init__(n_exp_times=1, p=p)


def test_drv_1():
    # m=2
    # a=2/(m*(m+1))=1/3
    n = sympy.Symbol('n')
    m = 10
    f1 = n / sympy.E
    f2 = 2 * n / (m * (m + 1))
    rv = DiscreteRandomVar(seg_p=[f1], laws=f2)
    x = range(1, m)
    y1 = []
    y2 = []
    for i in tqdm.tqdm(x):
        p1 = rv.get_prob(i / sympy.E, True)
        y1.append(p1)
    for i in tqdm.tqdm(x):
        p2 = rv.get_prob(i / sympy.E, False)
        y2.append(p2)
    plt.plot(list(x), y1)
    plt.plot(list(x), y2)
    plt.show()


def test_drv_2():
    x = sympy.Symbol('x')
    m = 100
    f1 = x / sympy.E
    f2 = 2 * x / (m * (m + 1))
    rv = DiscreteRandomVar(seg_p=[f1], laws=f2)
    f = rv.get_funcs_from_laws()
    return f


def test_drv_3():
    sp1 = [-1, 0, 1]
    f1 = [0, 0.3, 0.8, 1]
    rv1 = DiscreteRandomVar(seg_p=sp1, funcs=f1)
    p1_1 = rv1.get_prob(0.5, True)
    p1_2 = rv1.get_prob(0.5, False)
    x = sympy.Symbol('x')
    sp2 = [x / sympy.E]
    m = 100
    f2 = x * (x + 1) / (m * (m + 1))
    rv2 = DiscreteRandomVar(seg_p=sp2, funcs=f2)
    p2 = rv2.get_prob(5 / sympy.E, False)
    print(p1_1, p1_2)
    print(p2)


def test_drv_4():
    x = sympy.Symbol('x')
    sp = [x / sympy.E]
    m = 100
    f1 = x * (x + 1) / (m * (m + 1))
    rv1 = DiscreteRandomVar(seg_p=sp, funcs=f1)
    l1 = rv1.get_laws_from_funcs()
    rv2 = DiscreteRandomVar(seg_p=sp, laws=l1)
    f2 = rv2.get_funcs_from_laws()
    print(f2 == f1)


def test_drv_5():
    b = BinomialDist(n_exp_times=4, p=sympy.Rational(1, 2))
    zo = ZeroOneDist(p=sympy.Rational(3, 4))
    zop0 = zo.get_prob(0)
    zop1 = zo.get_prob(1)
    bp0 = b.get_prob(0)
    bp1 = b.get_prob(1)
    bp2 = b.get_prob(2)
    bp3 = b.get_prob(3)
    return [zop0, zop1, bp0, bp1, bp2, bp3]


def test_drv_6():
    g = GeometricDist(sympy.Rational(1, 8))
    hg = HyperGeometricDist(10, 3, 5)
    gp0_0 = g.get_prob(x=0, include_success=True)
    gp1_0 = g.get_prob(x=1, include_success=True)
    gp0_1 = g.get_prob(x=0, include_success=False)
    gp1_1 = g.get_prob(x=1, include_success=False)
    hg0 = hg.get_prob(0)
    hg1 = hg.get_prob(1)
    hg2 = hg.get_prob(2)
    hg3 = hg.get_prob(3)
    hg4 = hg.get_prob(4)
    hg5 = hg.get_prob(5)
    return [[gp0_0, gp1_0], [gp0_1, gp1_1], [hg0, hg1, hg2, hg3, hg4, hg5]]


def test_drv_7():
    pd = PoissonDist(2)
    pp0 = pd.get_prob(0)
    pp1 = pd.get_prob(1)
    pp2 = pd.get_prob(2)
    return [pp0, pp1, pp2]


def test_drv_8():
    n = 10
    bd = BinomialDist(n_exp_times=n, p=sympy.Rational(1, 2))
    pd = bd.poisson_theorem()
    x = range(0, n)
    y1 = []
    y2 = []
    for i in x:
        y1.append(bd.get_prob(i))
        y2.append(pd.get_prob(i))
    plt.plot(list(x), y1)
    plt.plot(list(x), y2)
    plt.show()


if __name__ == '__main__':
    print('Done')
