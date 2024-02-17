import multiprocessing

# noinspection PyCompatibility

import sympy

from Funcs import list2func, func2list, func_gen


def taylor_expansion(x_symbol, num, x_target=0, rank=6):
    if type(num) is list:
        num = list2func(x_symbol, num)
    s = num.series(x_symbol, x_target, rank)
    new_s = s.args[0]
    for i in range(1, len(s.args) - 1):
        new_s += s.args[i]
    new_s_l = func2list(x_symbol, new_s)
    return new_s, new_s_l


def is_approach_zero_but_not_zero(num, x_symbol, x_target):
    f = list2func(x_symbol, num)
    if sympy.limit(f, x_symbol, x_target) == 0:
        return True
    else:
        return False


def equivalent_infinitesimal(num, x_symbol, x_target=0):
    if num[0] == 'sin':
        if is_approach_zero_but_not_zero(x_symbol, num[1], x_target):
            num = num[1]
    elif num[0] == 'tan':
        if is_approach_zero_but_not_zero(x_symbol, num[1], x_target):
            num = num[1]
    elif num[0] == 'ln' and num[1][0] == '+':
        if num[1][1] == 1:
            if is_approach_zero_but_not_zero(num[1][2], x_symbol, x_target):
                num = num[1][2]
        elif num[1][2] == 1:
            if is_approach_zero_but_not_zero(num[1][1], x_symbol, x_target):
                num = num[1][1]
    elif num[0] == 'exp':
        if is_approach_zero_but_not_zero(num[1], x_symbol, x_target):
            num = ['+', 1, num[1]]
    elif num[0] in ['/', '*']:
        for i in range(1, len(num)):
            if type(num[i]) is list:
                num[i] = equivalent_infinitesimal(num[i], x_symbol, x_target)
    return num


def limit_existed(func, x_symbol, x_target):
    f_limit = sympy.limit(func, x_symbol, x_target)
    l_existed = type(f_limit) not in [sympy.core.numbers.Infinity, sympy.calculus.util.AccumulationBounds,
                                      sympy.core.numbers.nan, sympy.core.numbers.NegativeInfinity,
                                      sympy.core.numbers.zoo, sympy.Limit, sympy.core.numbers.NaN]
    return f_limit, l_existed


def compound_function_replacement(num, f_inner, x_symbol, x_target=0, fi_target=None):
    if type(f_inner) is list:
        f_inner = list2func(x_symbol, f_inner)
    if fi_target is None:
        fi_target, target_valid = limit_existed(f_inner, x_symbol, x_target)
    else:
        target_valid = True
    if target_valid:
        if list2func(x_symbol, num) == f_inner:
            num = 'x'
        else:
            for i in range(1, len(num)):
                num[i], fi_target = compound_function_replacement(num[i], f_inner, x_symbol, x_target, fi_target)
    else:
        fi_target = x_target
    return num, fi_target


def limit_thread(fx, x, target, lim_temp, existed_temp):
    print('Process started.')
    try:
        lim, existed = limit_existed(fx, x, target)
        lim_temp.value = bytes(str(lim).replace(' ', ''), encoding='ascii')
        existed_temp.value = existed
        # print('x->', target, ' Limit judged.')
    except NotImplementedError as e:
        print('Error: ', e)
        reset_limit(lim_temp, existed_temp)
    except ValueError as e:
        print('Error: ', e)
        reset_limit(lim_temp, existed_temp)


def reset_limit(lim_temp, existed_temp):
    lim_temp.value = bytes('', encoding='ascii')
    existed_temp.value = False


def answers_selector(fx, x_symbol, x_target, the_answer):
    ta = str(the_answer).replace(' ', '')
    ta = ta.replace('**', '^')
    ta = ta.replace('*', '')
    ta = ta.replace('exp', 'e^')
    if len(ta) > 5:
        return False, ''
    else:
        direct_sub = fx.evalf(subs={x_symbol: x_target})
        if direct_sub == sympy.N(the_answer):
            return False, direct_sub
        else:

            return True, direct_sub


def find_funcs_have_limits():
    lim_temp = multiprocessing.Array('c', 32)
    existed_temp = multiprocessing.Value('b', False)
    x = sympy.Symbol('x')
    flag = True
    while flag:
        fl = func_gen(2)
        # print('Func generated.')
        # print(fl)
        fx = list2func(x, fl)
        # print('Object transformed.')
        # print(fx)
        if len(fx.free_symbols) > 0:
            reset_limit(lim_temp, existed_temp)
            lt_1 = multiprocessing.Process(target=limit_thread, args=(fx, x, 0, lim_temp, existed_temp))
            lt_1.start()
            lt_1.join(5)
            print('Process timeout.')
            lt_1.terminate()
            lim, existed = lim_temp.value.decode(encoding='ascii'), bool(existed_temp.value)
            if existed:
                print('x->0', fx, ' ->', lim)
                lim = sympy.parse_expr(lim)
                as_res, ds_res = answers_selector(fx, x, 0, lim)
                if as_res:
                    flag = False
                else:
                    print('Filtered by AS:', lim, ds_res)
            else:
                reset_limit(lim_temp, existed_temp)
                lt_2 = multiprocessing.Process(target=limit_thread, args=(fx, x, sympy.oo, lim_temp, existed_temp))
                lt_2.start()
                lt_2.join(5)
                print('Process timeout.')
                lt_2.terminate()
                lim, existed = lim_temp.value.decode(encoding='ascii'), bool(existed_temp.value)
                if existed:
                    print('x->∞', fx, ' ->', lim)
                    lim = sympy.parse_expr(lim)
                    as_res, ds_res = answers_selector(fx, x, sympy.oo, lim)
                    if as_res:
                        flag = False
                    else:
                        print('Filtered by AS:', lim, ds_res)
                else:
                    # print(fx, ' failed.')
                    print('Try Again.')
        else:
            # print(fx, ' failed.')
            print('Try Again.')


if __name__ == '__main__':
    x = sympy.Symbol('x')
    fx = x - sympy.E
    lim1, lim_existed = limit_existed(fx, x, 1)
    lim_str = str(lim1).replace(' ', '')
    lim_parsed = sympy.parse_expr(lim_str)
    answer_check, direct_s = answers_selector(fx, x, 1, lim_parsed)
