import numpy
import random


def mat_proto(dim, rank=None):
    if rank is None:
        rank = random.randint(round(dim / 2), dim)
    mat_list = []
    for i in range(0, rank):
        mat_row = [0] * dim
        mat_row[i] = 1
        mat_list.append(mat_row)
    while len(mat_list) < dim:
        mat_row = [0] * dim
        mat_list.append(mat_row)
    mat = numpy.array(mat_list)
    return mat


def et_once(mat):
    dim = mat.shape[0]
    rows = list(range(0, dim))
    op_type = random.choice(['switch', 'const_mul', 'times_add'])
    et_mat_list = numpy.identity(dim).tolist()
    # noinspection PyTypeChecker
    et_mat_list = [[int(elem) for elem in row_list] for row_list in et_mat_list]
    first_r_index = random.choice(rows)
    k = random.randint(2, 4)
    op_type = 'times_add'
    if op_type is 'const_mul':
        et_mat_list[first_r_index] = [elem * k for elem in et_mat_list[first_r_index]]
    else:
        rows.remove(first_r_index)
        second_r_index = random.choice(rows)
        first_r = et_mat_list[first_r_index]
        second_r = et_mat_list[second_r_index]
        if op_type is 'switch':
            et_mat_list[first_r_index] = second_r
            et_mat_list[second_r_index] = first_r
        else:
            et_mat_list[second_r_index][first_r.index(1)] = k
    et_mat_array = numpy.array(et_mat_list)
    if random.choice(['row', 'col']) is 'row':
        res_mat = numpy.matmul(et_mat_array, mat)
    else:
        res_mat = numpy.matmul(mat, et_mat_array)
    return res_mat


def generate_mat_by_et(dim=3, et_count=5):
    mat_p = mat_proto(dim, dim)
    mat = mat_p
    while et_count > 0:
        mat = et_once(mat)
        et_count -= 1
    return mat_p, mat


if __name__ is '__main__':
    res = generate_mat_by_et()
    print(res[0])
    print(res[1])
