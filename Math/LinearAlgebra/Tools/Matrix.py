import random
import numpy


def mat_conditions(mat_dim=2, mat_count=4, int_range_lb=-3, int_range_ub=3):
    mat_count = min(26, mat_count)
    conditions = {}
    for i in range(0, mat_count):
        a_int = 65 + i
        a_char = chr(a_int)
        mat = numpy.random.randint(int_range_lb, int_range_ub, size=(mat_dim, mat_dim))
        conditions[a_char] = mat
    return conditions


def mat_question(conditions, parent_op=None, max_depth=3, max_length=3):
    op_list = []

    # region get_op
    if max_depth > 2 and max_length > 2:
        op = random.choice(['+', '*'])
    elif max_depth == 1 or max_length == 1:
        if random.choice(['matr', 'expr']) == 'matr' or parent_op == 'T':
            return random.choice(list(conditions.keys()))
        else:
            return ['T', random.choice(list(conditions.keys()))]
    elif parent_op == 'T':
        op = random.choice(['+', '*'])
    else:
        op = random.choice(['+', '*', 'T'])
    op_list.append(op)
    # endregion

    # region get_operand
    if op in ['+', '*']:
        operand_count = random.randint(2, max_length)
    else:
        operand_count = 1
    for i in range(0, operand_count):
        if random.choice(['matr', 'expr']) == 'matr' or max_depth == 1 or max_length == 1:
            operand = random.choice(list(conditions.keys()))
        else:
            operand = mat_question(conditions, op, max_depth - 1, max_length - 1)
        op_list.append(operand)
    # endregion

    return op_list


def mat_operation(conditions, question):
    question_str = str(question)
    for i in range(1, len(question)):
        if type(question[i]) == list:
            question[i], qs = mat_operation(conditions, question[i])
        if type(question[i]) is str:
            question[i] = conditions[question[i]].copy()
        if i != 1:
            if question[0] == '*':
                question[1] = numpy.matmul(question[1], question[i])
            elif question[0] == '+':
                question[1] += question[i]
        elif question[0] == 'T':
            question[i] = question[i].transpose()
    return question[1], question_str
