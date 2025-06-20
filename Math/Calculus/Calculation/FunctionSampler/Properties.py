import sympy as sp


def is_differentiable(func, extra_param, x):
    x0 = extra_param
    # 计算右导数：lim(h->0+) [f(x+h) - f(x)]/h
    h = sp.Symbol('h')
    right_derivative = sp.limit((func.subs(x, x0 + h) - func.subs(x, x0)) / h, h, 0, dir='+')

    # 计算左导数：lim(h->0-) [f(x+h) - f(x)]/h
    left_derivative = sp.limit((func.subs(x, x0 + h) - func.subs(x, x0)) / h, h, 0, dir='-')

    # 判断可导性
    is_diff = (right_derivative == left_derivative) and not (right_derivative == -sp.oo or right_derivative == sp.oo)
    return is_diff


def exist_partial_derivatives(func, extra_param, x):
    x_var, y_var = x[0], x[1]
    x0, y0 = extra_param[0], extra_param[1]
    x_diff = is_differentiable(func=func.subs(y_var, y0), extra_param=x0, x=x_var)
    if x_diff:
        y_diff = is_differentiable(func=func.subs(x_var, x0), extra_param=y0, x=y_var)
        if y_diff:
            return True
    return False


def is_continuous(func, extra_param, x):
    x0 = extra_param
    # 1. 计算函数在x0处的值
    f_at_x0 = func.subs(x, x0)
    f_at_x0_abs = abs(f_at_x0)
    if f_at_x0_abs == sp.nan or f_at_x0_abs == sp.oo:
        return False
    else:
        return True


def is_differentiable_multivariate(func, extra_param, x):
    x_var, y_var = x[0], x[1]
    x0, y0 = extra_param[0], extra_param[1]
    x_offset, y_offset = x0 - 0, y0 - 0
    x0, y0 = sp.S(0), sp.S(0)
    func2 = func.subs({x_var: x_var + x_offset, y_var: y_var + y_offset})

    dx, dy = sp.symbols('dx dy', real=True)
    f_at_xy = func2.subs({x_var: x0, y_var: y0})
    f_at_xy_dxdy = func2.subs({x_var: x0 + dx, y_var: y0 + dy})
    fx_unary = func2.subs(y_var, y0)
    fx_at_xy = compute_partial_derivative(fx_unary, x_var, x0)
    fy_unary = func2.subs(x_var, x0)
    fy_at_xy = compute_partial_derivative(fy_unary, y_var, y0)
    numerator = f_at_xy_dxdy - f_at_xy - fx_at_xy * dx - fy_at_xy * dy
    rho = sp.sqrt(dx ** 2 + dy ** 2)
    limit_expr = numerator / rho

    limit_expr_polar, r, t = to_polar(func=limit_expr, x=dx, y=dy)

    res = sp.simplify(sp.limit(limit_expr_polar, r, 0))
    return res == sp.S(0)


def to_polar(func, x, y):
    r, t = sp.symbols('r t', positive=True)
    return func.subs({x: r * sp.cos(t), y: r * sp.sin(t)}), r, t


def compute_partial_derivative(func, var, point_val):
    h = sp.symbols('h', real=True)
    diff_expr = (func.subs(var, point_val + h) - func.subs(var, point_val)) / h
    return sp.limit(diff_expr, h, 0)


def exist_limit(func, extra_param, x):
    x0 = extra_param
    result_r = sp.limit(func, x, x0, dir='+')
    result_l = sp.limit(func, x, x0, dir='-')
    print(result_r, result_l)
    is_valid = result_r.is_Number and result_r.is_finite and result_r == result_l
    # todo: limit has bug!!!
    return is_valid


def is_continuous_multivariate(func, extra_param, x):
    pass


def is_periodic(func, extra_param, x):
    pass


def is_integrable(func, extra_param, x):
    pass


def is_2nd_order_partial_derivative_continuous():
    pass


def is_odd():
    pass


def is_even():
    pass


def is_tangent_to_line():
    pass


def is_anomalous_integral_convergent():
    pass


if __name__ == '__main__':
    x = sp.Symbol('x')
    y = sp.Symbol('y')
    f1 = sp.sympify('sin(1/x)')
    f2 = sp.sympify('1/x')
    f3 = sp.sympify('sin(1/x)/x')
    f4 = sp.sympify('Piecewise((2, x < 0),(5, x > 0),(0, Eq(x,0)))')
    x0 = sp.S(0)
    y0 = sp.S(0)
    exist_limit(func=f4, extra_param=x0, x=x)
    print('Done')
