import sympy
from sympy import is_increasing, Interval
from sympy.solvers.inequalities import solve_univariate_inequality


def left_zero_right_one(var, func=None, funcs=None):
    if funcs is not None:
        left = sympy.limit(funcs[0], var, -sympy.oo)
        right = sympy.limit(funcs[1], var, sympy.oo)
    elif func is not None:
        left = sympy.limit(func, var, -sympy.oo)
        right = sympy.limit(func, var, sympy.oo)
    else:
        left = -1
        right = -1
    if left == 0 and right == 1:
        return True
    else:
        return False


def right_continuous(var, funcs, seg_points, seg_types):
    for i in range(0, len(seg_points)):
        seg_point = seg_points[i]
        seg_type = seg_types[i]
        r_lim = sympy.limit(funcs[i + 1], var, seg_point)
        f_val = sympy.sympify(funcs[seg_type]).evalf(subs={var: seg_point})
        if r_lim.evalf() != f_val:
            return False
    return True


def non_negative(var, func, valid_domain):
    if valid_domain[1][0] == 'closed':
        vd_lb = sympy.GreaterThan(var, valid_domain[0][0])
    else:
        vd_lb = sympy.StrictGreaterThan(var, valid_domain[0][0])
    if valid_domain[1][1] == 'closed':
        vd_ub = sympy.LessThan(var, valid_domain[0][1])
    else:
        vd_ub = sympy.StrictLessThan(var, valid_domain[0][1])
    vd = sympy.And(vd_lb, vd_ub)
    smaller_than_0 = solve_univariate_inequality(func < 0, var)
    smaller_than_0 = sympy.simplify(sympy.And(smaller_than_0, vd))
    smaller_than_0 = domain_validity(smaller_than_0)
    larger_than_1 = solve_univariate_inequality(func > 1, var)
    larger_than_1 = sympy.simplify(sympy.And(larger_than_1, vd))
    larger_than_1 = domain_validity(larger_than_1)
    if smaller_than_0 or larger_than_1:
        return False
    else:
        return True


def domain_validity(domain):
    if domain:
        lb = domain.args[0].args[1]
        lb_type = type(domain.args[0])
        ub = domain.args[1].args[1]
        ub_type = type(domain.args[1])
        if lb == ub:
            if lb_type is sympy.core.GreaterThan and ub_type is sympy.core.LessThan:
                return True
            else:
                return False
        elif lb < ub:
            return True
        else:
            return False
    else:
        return False


def monotonic_non_dec(var, func, valid_domain):
    if valid_domain[1][0] == 'closed' and valid_domain[1][1] == 'closed':
        vd_int = Interval(valid_domain[0][0], valid_domain[0][1])
    elif valid_domain[1][0] == 'opened' and valid_domain[1][1] == 'closed':
        vd_int = Interval.Lopen(valid_domain[0][0], valid_domain[0][1])
    elif valid_domain[1][0] == 'closed' and valid_domain[1][1] == 'opened':
        vd_int = Interval.Ropen(valid_domain[0][0], valid_domain[0][1])
    else:
        vd_int = Interval.open(valid_domain[0][0], valid_domain[0][1])
    return is_increasing(func, vd_int, var)


def test_1():
    x = sympy.Symbol('x')
    f1 = 1 / (1 + x ** 2)
    f2 = (3 / 4) + (sympy.atan(x) / (2 * sympy.pi))
    f3 = [0, x / (1 + x)]
    f4 = 1 + (2 * sympy.atan(x) / sympy.pi)
    r1 = left_zero_right_one(var=x, func=f1)
    r2 = left_zero_right_one(var=x, func=f2)
    r3 = left_zero_right_one(var=x, funcs=f3)
    r4 = left_zero_right_one(var=x, func=f4)


def test_2():
    x = sympy.Symbol('x')
    f1 = [0, x / (1 + x)]
    sp1 = [0]
    st1 = [0]

    f2 = [0, 1 / 2, 1 - sympy.exp(-x)]
    sp2 = [0, 1]
    st2 = [1, 2]

    f3 = [0, sympy.sin(x), 1]
    sp3 = [0, sympy.pi / 2]
    st3 = [1, 1]
    r1 = right_continuous(x, f1, sp1, st1)
    r2 = right_continuous(x, f2, sp2, st2)
    r3 = right_continuous(x, f3, sp3, st3)


def test_3():
    x = sympy.Symbol('x')
    f = sympy.sin(x)
    d = [
        [0, sympy.pi / 2],
        ['closed', 'closed']
    ]
    non_negative(x, f, d)


def test_4():
    x = sympy.Symbol('x')
    f = sympy.sin(x)
    d = [
        [0, sympy.pi / 2],
        ['closed', 'closed']
    ]
    res = monotonic_non_dec(x, f, d)
    return res


if __name__ == '__main__':
    r = test_4()
    print('Done')
