import numpy
import tqdm
import sympy
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')


def trunc(values, decs=0):
    return numpy.trunc(values * 10 ** decs) / (10 ** decs)


class RandomVar:
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

    def get_prob(self, x, use_law=False):
        p = 0
        if self.rv_type == 'finite':
            for i in range(0, len(self.regions) - 1):
                region = self.regions[i]
                if region[0] <= x:
                    if use_law:
                        p += self.dist_laws[i]
                    if x < region[1]:
                        if not use_law:
                            p = self.dist_funcs[i]
                        break
            if self.regions[-1][0] <= x < self.regions[-1][1]:
                p = 1
        else:
            n0 = 0
            n = list(self.regions.free_symbols)[0]
            if len(self.cache) == 0:
                self.cache.append(0.0)
            while self.regions.evalf(subs={n: n0}) <= x.evalf():
                if use_law:
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
            if not use_law:
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


def test_drv_1():
    # m=2
    # a=2/(m*(m+1))=1/3
    n = sympy.Symbol('n')
    m = 10
    f1 = n / sympy.E
    f2 = 2 * n / (m * (m + 1))
    rv = RandomVar(seg_p=[f1], laws=f2)
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
    rv = RandomVar(seg_p=[f1], laws=f2)
    f = rv.get_funcs_from_laws()
    return f


def test_drv_3():
    sp1 = [-1, 0, 1]
    f1 = [0, 0.3, 0.8, 1]
    rv1 = RandomVar(seg_p=sp1, funcs=f1)
    p1_1 = rv1.get_prob(0.5, True)
    p1_2 = rv1.get_prob(0.5, False)
    x = sympy.Symbol('x')
    sp2 = [x / sympy.E]
    m = 100
    f2 = x * (x + 1) / (m * (m + 1))
    rv2 = RandomVar(seg_p=sp2, funcs=f2)
    p2 = rv2.get_prob(5 / sympy.E, False)
    print(p1_1, p1_2)
    print(p2)


def test_drv_4():
    x = sympy.Symbol('x')
    sp = [x / sympy.E]
    m = 100
    f1 = x * (x + 1) / (m * (m + 1))
    rv1 = RandomVar(seg_p=sp, funcs=f1)
    l1 = rv1.get_laws_from_funcs()
    rv2 = RandomVar(seg_p=sp, laws=l1)
    f2 = rv2.get_funcs_from_laws()
    print(f2 == f1)


if __name__ == '__main__':
    test_drv_1()
    print('Done')
