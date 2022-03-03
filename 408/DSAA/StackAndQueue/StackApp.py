match_dict = {'(': ')', '[': ']', '{': '}'}


def parentheses_match(p_str):
    stack = []
    for char in p_str:
        if char in ['(', '[', '{']:
            stack.append(char)
        elif len(stack) > 0 and char is match_dict[stack[-1]]:
            stack.pop(-1)
        else:
            return False
    if len(stack) is 0:
        return True
    else:
        return False


op_priorities = {'*': 2, '/': 2, '+': 1, '-': 1}
parentheses_case = {True: ['(', ')'], False: [')', '(']}


def stop_loop(st_top, scanned_op, reverse):
    if op_priorities[st_top] < op_priorities[scanned_op]:
        return True
    elif op_priorities[st_top] == op_priorities[scanned_op]:
        if reverse:
            return False
        else:
            return True
    else:
        return False


def polish_notation(infix_expr, reverse=False):
    polish_n = []
    stack = []
    infix_expr_copy = infix_expr.copy()
    if not reverse:
        infix_expr_copy.reverse()
    for char in infix_expr_copy:
        if char is parentheses_case[reverse][0]:
            stack.append(char)
        elif char is parentheses_case[reverse][1]:
            while len(stack) > 0:
                elem = stack.pop(-1)
                if elem is parentheses_case[reverse][0]:
                    break
                else:
                    polish_n.append(elem)
        elif char in ['+', '-', '*', '/']:
            while len(stack) > 0:
                if stack[-1] is parentheses_case[reverse][0] or stop_loop(stack[-1], char,
                                                                          reverse):
                    break
                else:
                    elem = stack.pop(-1)
                    polish_n.append(elem)
            stack.append(char)
        else:
            polish_n.append(char)
    while len(stack) > 0:
        polish_n.append(stack.pop(-1))
    if not reverse:
        polish_n.reverse()
    return polish_n


def infix_calculation(infix_expr, reverse=False):
    operand_stack = []
    op_stack = []
    infix_expr_copy = infix_expr.copy()
    if not reverse:
        infix_expr_copy.reverse()
    for char in infix_expr_copy:
        if char is parentheses_case[reverse][0]:
            op_stack.append(char)
        elif char is parentheses_case[reverse][1]:
            while len(op_stack) > 0:
                elem = op_stack.pop(-1)
                if elem is parentheses_case[reverse][0]:
                    break
                else:
                    operand_2 = operand_stack.pop(-1)
                    operand_1 = operand_stack.pop(-1)
                    if reverse:
                        operand_res = str(eval(operand_1 + elem + operand_2))
                    else:
                        operand_res = str(eval(operand_2 + elem + operand_1))
                    operand_stack.append(operand_res)
        elif char in ['+', '-', '*', '/']:
            while len(op_stack) > 0:
                if op_stack[-1] is parentheses_case[reverse][0] or stop_loop(
                        op_stack[-1],
                        char,
                        reverse
                ):
                    break
                else:
                    elem = op_stack.pop(-1)
                    operand_2 = operand_stack.pop(-1)
                    operand_1 = operand_stack.pop(-1)
                    if reverse:
                        operand_res = str(eval(operand_1 + elem + operand_2))
                    else:
                        operand_res = str(eval(operand_2 + elem + operand_1))
                    operand_stack.append(operand_res)
            op_stack.append(char)
        else:
            operand_stack.append(char)

    while len(op_stack) > 0:
        elem = op_stack.pop(-1)
        operand_2 = operand_stack.pop(-1)
        operand_1 = operand_stack.pop(-1)
        if reverse:
            operand_res = str(eval(operand_1 + elem + operand_2))
        else:
            operand_res = str(eval(operand_2 + elem + operand_1))
        operand_stack.append(operand_res)
    return eval(operand_stack.pop(-1))


if __name__ is '__main__':
    i_expr = ['(', '1', '+', '(', '(', '2', '+', '3', ')', '*', '4', ')', ')', '/', '5']
    res = infix_calculation(i_expr, True)
    print(res)
