import tqdm
import sympy
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')


class RandomVar:
    dist_func = None
    regions = None
    rv_type = None
    cache = None

    def __init__(self, funcs, seg_points=None):
        self.dist_func = funcs
        if type(seg_points) is list:
            self.rv_type = 'finite'
            self.regions = []
            for i in range(0, len(seg_points)):
                point = seg_points[i]
                if i == 0:
                    region = [-sympy.oo, point]
                else:
                    region = [seg_points[i - 1], point]
                self.regions.append(region)
            self.regions.append([seg_points[-1], sympy.oo])
        elif hasattr(seg_points, 'free_symbols') and len(seg_points.free_symbols) > 0:
            self.rv_type = 'infinite'
            self.regions = seg_points
            self.cache = []

    def get_prob(self, x):
        p = 0
        if self.rv_type == 'finite':
            for i in range(0, len(self.regions) - 1):
                region = self.regions[i]
                if region[0] <= x < region[1]:
                    p += self.dist_func[i]
            if self.regions[-1][0] <= x < self.regions[-1][1]:
                p = 1
        else:
            n0 = 0
            n = list(self.regions.free_symbols)[0]
            if len(self.cache) == 0:
                self.cache.append(0.0)
            while self.regions.evalf(subs={n: n0}) <= x.evalf():
                if len(self.cache) >= n0 + 1:
                    pass
                else:
                    self.cache.append(self.cache[-1] + self.dist_func.evalf(subs={n: n0}))
                p = self.cache[n0]
                if self.cache[n0] >= 1:
                    self.cache[n0] = 1
                    p = 1
                    break
                n0 += 1

        if type(p) is not float:
            p = float(p)
        return p


# m=2
# a=2/(m*(m+1))=1/3
x = sympy.Symbol('x')
m = 100
f1 = x / sympy.E
f2 = 2 * x / (m * (m + 1))

rv = RandomVar(f2, f1)
x = range(1, 100)
y = []
for i in tqdm.tqdm(x):
    y.append(rv.get_prob(i / sympy.E))

fig = plt.figure()

plt.plot(x, y)

plt.show()
print('Done')
