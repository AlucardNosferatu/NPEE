from multiprocessing.spawn import freeze_support

import sympy

from Limits import taylor_expansion, compound_function_replacement, find_funcs_have_limits
from Funcs import list2func, func2list


def test_1():
    x_symbol = sympy.Symbol('x')
    # "((e^(x^2))-1)/(cos(x)-1)"
    exp_gl_1 = ['/', ['-', ['**', 'e', ['**', 'x', 2]], 1], ['-', ['cos', 'x'], 1]]
    function = list2func(x_symbol, exp_gl_1)
    lim = sympy.limit(function, x_symbol, 0)
    print(lim)


def test_2():
    x = sympy.Symbol('x')
    fl = func2list(x, sympy.sin(x))
    # noinspection PyTypeChecker
    fs, fsl = taylor_expansion(x, fl)
    fgl = list2func(x, fsl)
    print('Done')


def test_3():
    x = sympy.Symbol('x')
    func = (sympy.ln(1 + sympy.sin(x) ** 2) - 6 * (((2 - sympy.cos(x)) ** sympy.Rational(1, 3)) - 1)) / (x ** 4)
    lim1 = sympy.limit(func, x, 0)
    func_l = func2list(x, func)
    func23, func_l[2][3] = taylor_expansion(x, func_l[2][3])
    func_new = list2func(x, func_l)
    lim2 = sympy.limit(func_new, x, 0)
    print(lim1 == lim2)


def test_4():
    x = sympy.Symbol('x')
    gx = sympy.sin(x)
    fx = sympy.exp(sympy.sin(x)) + sympy.sin(x)
    fx_l = func2list(x, fx)
    target = sympy.oo
    fx_l_new, new_target = compound_function_replacement(fx_l, gx, x, target)
    fx_new = list2func(x, fx_l_new)
    print('x->', target)
    print(fx)
    print('x->', new_target)
    print(fx_new)


def test_5():
    freeze_support()
    while True:
        print('New sequence initiated.')
        find_funcs_have_limits()
        print()
        print()
        print()
        print()
        print()


if __name__ == '__main__':
    test_5()
