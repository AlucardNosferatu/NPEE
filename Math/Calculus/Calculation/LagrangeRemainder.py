from sympy import symbols, factorial, diff, exp


def get_lr_bound(x0, x1, degree, f, x_symbol):
    lr = diff(f, x_symbol, degree + 1) * ((x1 - x0) ** (degree + 1)) / factorial(degree + 1)
    lrb_x1 = lr.evalf(subs={x_symbol: x1})
    lrb_x0 = lr.evalf(subs={x_symbol: x0})
    return lrb_x0, lrb_x1


if __name__ == '__main__':
    x = symbols('x')
    f_ = exp(x)
    x0_ = 2
    x1_ = 1.45
    degree_list = [2, 3, 4, 5]
    lrb_list = []
    for degree_ in degree_list:
        lrb = get_lr_bound(x0=x0_, x1=x1_, degree=degree_, f=f_, x_symbol=x)
        lrb_list.append(lrb)
    print('Done')
