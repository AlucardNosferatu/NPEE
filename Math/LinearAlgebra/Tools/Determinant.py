import numpy

from Matrix import mat_operation, mat_question, mat_conditions


def det_problems(mat=None):
    if mat is None:
        mat = numpy.random.randint(0, 10, size=(3, 3))
        while numpy.linalg.matrix_rank(mat) != 3:
            mat = numpy.random.rand(3, 3)
    mat_d = str(int(numpy.round(numpy.linalg.det(mat))))
    return [mat], mat_d, 'det'


def cofactor_problems():
    mat, mat_d, _ = det_problems()
    selected_row = numpy.random.choice([0, 1, 2], 1).max()
    mat = mat[0].tolist()
    swap_row = numpy.random.randint(0, 10, size=(1, 3))
    coefficients = mat[selected_row]
    p_text = str(coefficients[0]) + '*A' + str(selected_row + 1) + '1+' + \
             str(coefficients[1]) + '*A' + str(selected_row + 1) + '2+' + \
             str(coefficients[2]) + '*A' + str(selected_row + 1) + '3'
    p_text = 'Need to solve:\n' + p_text
    mat[selected_row] = swap_row.tolist()[0]
    # noinspection PyTypeChecker
    mat = numpy.array(mat)
    return [mat, p_text], mat_d, 'cof'


def problem_interface(conditions, the_answer, problem_type):
    print('Given:')
    for condition in conditions:
        print(condition)
    if problem_type == 'det':
        print('Calculate the determinant.')
    elif problem_type == 'cof':
        print('Calculate the formula above.')
    user_input = ''
    first_try = True
    while user_input != 'fuck' and user_input != the_answer:
        if not first_try:
            print('Incorrect.')
        else:
            first_try = False
        user_input = input()
        if user_input.startswith('mat:'):
            user_input = user_input[4:]
            ui_rows = user_input.split(';')
            ui_rows = [row.split(',') for row in ui_rows]
            user_input = numpy.array(ui_rows)
    if user_input == the_answer:
        print('Correct! The answer is:')
        print(the_answer)
    elif user_input == 'fuck':
        print('The answer is:')
        print(the_answer)


# m, m_d, p_type = det_problems()
# p, ans, p_type = cofactor_problems()
# problem_interface(p, ans, p_type)
if __name__ == '__main__':
    conditions = mat_conditions()
    question = mat_question(conditions, None, 5, 3)
    res, qs = mat_operation(conditions, question)
    for key in conditions:
        print(key)
        print(conditions[key])
    print()
    print()
    print(qs)
    print(res)
