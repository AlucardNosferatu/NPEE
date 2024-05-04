import sympy as sp


def standardize_equation(eq):
    # 将方程移项，化为右侧等于0的形式
    return eq.lhs - eq.rhs


def lagrangian_function(obj_func, cons):
    # 创建拉格朗日乘子 lambda
    lambda_vars = list(sp.symbols('lambda:' + str(len(cons))))
    # 创建拉格朗日函数
    lagrangian = obj_func
    for i, eq in enumerate(cons):
        standardized_eq = standardize_equation(eq)
        lagrangian = lagrangian + lambda_vars[i] * standardized_eq
    return lagrangian, lambda_vars


def partial_derivatives(multi_var_func, ind_vars):
    # 创建一个空列表，用于存储偏导数表达式
    partials = []
    # 对于B中的每个符号
    for symbol in ind_vars:
        # 求A关于当前符号的偏导数
        partial = sp.diff(multi_var_func, symbol)
        # 将偏导数表达式添加到列表中
        partials.append(partial)
    return partials


def l_solve(obj_func: sp.Expr, cons):
    print("目标函数:", obj_func)
    [print("约束条件:", c) for c in cons]
    ind_vars_ = obj_func.free_symbols
    for c in cons:
        ind_vars_ = ind_vars_.union(c.free_symbols)
    ind_vars_ = list(ind_vars_)
    # 获取拉格朗日函数和拉格朗日乘子列表
    l_func, l_m = lagrangian_function(obj_func, cons)
    print("拉格朗日函数:", l_func)
    print("拉格朗日乘子列表:", l_m)
    ind_vars_ += l_m
    l_func_pd_list = partial_derivatives(l_func, ind_vars_)
    [print("拉格朗日函数对", ind_var, '的偏导数:', l_func_pd) for l_func_pd, ind_var in zip(l_func_pd_list, ind_vars_)]
    l_func_pd_list = [sp.Eq(l_func_pd, 0) for l_func_pd in l_func_pd_list]
    solutions = sp.solve(f=tuple(l_func_pd_list))
    if type(solutions) is not list:
        solutions = [solutions]
    func_vals = []
    for i, solution in enumerate(solutions):
        obj_func_ = obj_func
        print("拉格朗日乘数法求出解:", i + 1)
        for key in solution.keys():
            print("{}={}".format(key, solution[key]), end='  ')
            if key in obj_func_.free_symbols:
                obj_func_ = obj_func_.subs({key: solution[key]})
        func_vals.append(obj_func_)
        print('')
        print("函数值={}".format(obj_func_))
    max_val = max(func_vals)
    min_val = min(func_vals)
    print('最大值:', max_val, '最小值:', min_val)
    return solutions, func_vals, max_val, min_val


if __name__ == '__main__':
    # 示例用法
    # 创建符号变量
    x, y, z = sp.symbols('x y z')
    # 定义目标函数
    obj_func__ = x + y + z
    # 定义约束条件方程列表
    cons_ = [sp.Eq(x ** 2 + y ** 2 + z ** 2, sp.Rational(27, 4))]
    s, v, max_v, min_v = l_solve(obj_func__, cons_)
    print('Done')
