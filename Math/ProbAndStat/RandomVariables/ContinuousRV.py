import sympy


class ContinuousRandomVar:
    var_symbol = None
    prob_dens_func = None
    cum_dist_func = None
    piecewise = None

    def __init__(self, pdf=None, cdf=None):
        if pdf is not None:
            self.prob_dens_func = pdf
            self.var_symbol = list(self.prob_dens_func.free_symbols)[0]
            if type(self.prob_dens_func) is sympy.Piecewise:
                self.piecewise = True
                fix_int_list = []
                prev_ub = None
                cdf_list = []
                for i, piece in enumerate(self.prob_dens_func.args):
                    cdf_list, fix_int_list, prev_ub = self.process_piece_by_piece(
                        cdf_list,
                        fix_int_list,
                        i,
                        piece,
                        prev_ub
                    )
                foolish_passing = 'sympy.Piecewise('
                for i in range(0, len(cdf_list)):
                    foolish_passing += 'cdf_list[' + str(i) + ']'
                    if i < len(cdf_list) - 1:
                        foolish_passing += ','
                foolish_passing += ')'
                self.cum_dist_func = eval(foolish_passing)
            else:
                self.piecewise = False
                self.cum_dist_func = sympy.integrate(
                    self.prob_dens_func,
                    (self.var_symbol, -sympy.oo, self.var_symbol)
                )
            self.cum_dist_func = sympy.simplify(self.cum_dist_func)
        elif cdf is not None:
            self.piecewise = type(self.cum_dist_func) is sympy.Piecewise
            self.cum_dist_func = cdf
            self.var_symbol = list(self.cum_dist_func.free_symbols)[0]
            self.prob_dens_func = sympy.diff(
                self.cum_dist_func,
                self.var_symbol
            )
            self.prob_dens_func = sympy.simplify(self.prob_dens_func)
        else:
            raise TypeError('PMF or CDF must be specified!')

    def process_piece_by_piece(self, cdf_list, fix_int_list, i, piece, prev_ub):
        pdf_p = piece.args[0]
        if type(piece.args[1]) not in [
            sympy.LessThan,
            sympy.StrictLessThan,
            sympy.GreaterThan,
            sympy.StrictGreaterThan
        ]:
            ub = sympy.oo
        else:
            ub = piece.args[1].args[1]
        if i == 0:
            lb = -sympy.oo
        else:
            lb = prev_ub
        fix_int = sympy.integrate(
            pdf_p,
            (self.var_symbol, lb, ub)
        )
        if i != 0:
            fix_int += fix_int_list[i - 1]
        fix_int_list.append(fix_int)
        cdf_p = sympy.integrate(
            pdf_p,
            (self.var_symbol, lb, self.var_symbol)
        )
        if i != 0:
            cdf_p += fix_int_list[i - 1]
        # noinspection PyUnresolvedReferences
        cdf_p = sympy.functions.elementary.piecewise.ExprCondPair(cdf_p, piece.args[1])
        cdf_list.append(cdf_p)
        prev_ub = ub
        return cdf_list, fix_int_list, prev_ub

    def get_prob_less_than(self, x):
        return self.cum_dist_func.subs(self.var_symbol, x)

    def get_prob_between(self, a, b):
        a_prob = self.cum_dist_func.subs(self.var_symbol, a)
        b_prob = self.cum_dist_func.subs(self.var_symbol, b)
        return b_prob - a_prob


class UniformDist(ContinuousRandomVar):
    upper_bound = None
    lower_bound = None

    def __init__(self, a, b):
        self.lower_bound = min(a, b)
        self.upper_bound = max(a, b)
        x = sympy.Symbol('x')
        pdf = sympy.Piecewise(
            (0, x < self.lower_bound),
            (
                sympy.sympify(1 / (self.upper_bound - self.lower_bound)),
                x < self.upper_bound
            ),
            (0, True),
        )
        super().__init__(pdf=pdf)


class ExponentialDist(ContinuousRandomVar):
    lambda_coe = None

    def __init__(self, lambda_coe):
        self.lambda_coe = lambda_coe
        x = sympy.Symbol('x')
        pdf = sympy.Piecewise(
            (0, x <= 0),
            (
                self.lambda_coe * sympy.exp(-self.lambda_coe * x),
                True
            )
        )
        super().__init__(pdf=pdf)


class NormalDist(ContinuousRandomVar):
    sigma_std_dev = None
    mu_exp_val = None

    def __init__(self, ssd, mev):
        self.sigma_std_dev = ssd
        self.mu_exp_val = mev
        x = sympy.Symbol('x')
        pdf = sympy.exp(
            -((x - self.mu_exp_val) ** 2) / (2 * (self.sigma_std_dev ** 2))
        ) / (sympy.sqrt(2 * sympy.pi) * self.sigma_std_dev)
        super().__init__(pdf=pdf)


def test_1():
    x = sympy.Symbol('x')
    pdf_1 = sympy.Piecewise(
        (0, x < -1),
        (1 + x, x < 0),
        (1 - x, x < 1),
        (0, True)
    )
    pdf_2 = sympy.exp(-(x ** 2) / 2) / sympy.sqrt(2 * sympy.pi)
    crv1_1 = ContinuousRandomVar(pdf=pdf_1)
    cdf_1 = crv1_1.cum_dist_func
    crv1_2 = ContinuousRandomVar(cdf=cdf_1)
    crv2_1 = ContinuousRandomVar(pdf=pdf_2)
    cdf_2 = crv2_1.cum_dist_func
    crv2_2 = ContinuousRandomVar(cdf=cdf_2)

    # p1 = crv1_1.get_prob_less_than(-2)
    # p2 = crv1_1.get_prob_less_than(sympy.Rational(1, 4))
    # p3 = crv1_1.get_prob_between(-2, sympy.Rational(1, 4))
    return [crv1_1, crv1_2, crv2_1, crv2_2]


def test_2():
    x = sympy.Symbol('x')
    cdf_1 = sympy.Piecewise(
        (0, x < 0),
        (2 * sympy.atan(x) / sympy.pi, True)
    )
    pdf_1 = sympy.Piecewise(
        (0, x < 0),
        (sympy.Rational(1, 3), x <= 1),
        (0, x < 3),
        (sympy.Rational(2, 9), x <= 6),
        (0, True)
    )
    crv1 = ContinuousRandomVar(cdf=cdf_1)
    crv2 = ContinuousRandomVar(pdf=pdf_1)
    return crv1, crv2


def test_3():
    u = UniformDist(a=1, b=2)
    res1 = u.get_prob_between(1, 2)
    e = ExponentialDist(lambda_coe=2)
    res2 = e.get_prob_between(3, 5)
    res3 = e.get_prob_less_than(0.5)
    n = NormalDist(ssd=sympy.Rational(3, 4), mev=sympy.Rational(1, 4))
    res4 = n.get_prob_less_than(0)
    return res1, res2, res3, res4


if __name__ == '__main__':
    res = test_3()
    print('Done')
