import random

import sympy

var_z = sympy.Symbol('z')
op_a = ['sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'exp', 'ln']
op_abcd = ['+', '-', '*', '/', '**']
upper_bound = {'+': 3, '-': 3, '*': 3, '/': 2, '**': 2}
f_op_a = {
    type(sympy.sin(var_z)): 'sin',
    type(sympy.cos(var_z)): 'cos',
    type(sympy.tan(var_z)): 'tan',
    type(sympy.cot(var_z)): 'cot',
    type(sympy.sec(var_z)): 'sec',
    type(sympy.csc(var_z)): 'csc',
    type(sympy.exp(var_z)): 'exp',
    type(sympy.ln(var_z)): 'ln'

}
f_op_abcd = {
    type(2 + var_z): '+',
    type(2 * var_z): '*',
    type(2 ** var_z): '**'
}


def type_conversion(x_symbol, num, l2f=True):
    if l2f:
        if type(num) is list:
            num = list2func(x_symbol, num)
        elif num == 'x':
            num = x_symbol
        elif num == 'e':
            num = sympy.E
        elif num == 'pi':
            num = sympy.pi
    else:
        if type(num) in f_op_a or type(num) in f_op_abcd:
            num = func2list(x_symbol, num)
        elif num == x_symbol:
            num = 'x'
        elif num == sympy.E:
            num = 'e'
        elif num == sympy.pi:
            num = 'pi'
        elif num.is_Number:
            if num.is_zero:
                num = 0
            elif num.is_integer:
                num = int(num)
            else:
                num = ['/', num.numerator, num.denominator]
    return num


def list2func(x_symbol, exp_gl):
    f = 0
    op = exp_gl[0]
    if op in op_a:
        num = exp_gl[1]
        num = type_conversion(x_symbol, num)
        f = eval('sympy.' + op + '(num)')
    elif op in op_abcd:
        f = exp_gl[1]
        f = type_conversion(x_symbol, f)
        for i in range(2, len(exp_gl)):
            num = exp_gl[i]
            num = type_conversion(x_symbol, num)
            if op == '/':
                try:
                    f = sympy.Rational(f, num)
                except TypeError:
                    f = f / num
            else:
                f = eval('f' + op + 'num')
    f = sympy.simplify(f)
    return f


def func2list(x_symbol, f):
    func_list = []
    op = type(f)
    if op in f_op_a:
        func_list.append(f_op_a[op])
        func_list.append(type_conversion(x_symbol, f.args[0], False))
    elif op in f_op_abcd:
        func_list.append(f_op_abcd[op])
        for i in range(0, len(list(f.args))):
            func_list.append(type_conversion(x_symbol, f.args[i], False))
    elif op.is_Number:
        func_list.append('*')
        func_list.append(type_conversion(x_symbol, op, False))
        func_list.append(1)
    return func_list


def func_gen(depth=5):
    f_list = []
    if depth == 0:
        operand = random.choice(['x', 'e', 'pi', random.randint(2, 10)])
        return operand
    else:
        op_type = random.choice(['a', 'abcd', 'abcd'])
        if op_type == 'a':
            op = random.choice(op_a)
            f_list.append(op)
            operand = func_gen(depth - 1)
            f_list.append(operand)
        elif op_type == 'abcd':
            op = random.choice(op_abcd)
            f_list.append(op)
            operand_count = random.randint(2, upper_bound[op])
            for i in range(0, operand_count):
                operand = func_gen(depth - 1)
                f_list.append(operand)

    return f_list
