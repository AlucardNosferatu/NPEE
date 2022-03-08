import numpy

from ElemTrans import mat_proto, generate_mat_by_et
from Matrix import mat_conditions


def is_invertible(mat):
    det = numpy.linalg.det(mat)
    return det != 0


def upper_tri_mat(mat: numpy.ndarray):
    dim = mat.shape[0]
    for j in range(0, dim):
        for i in range(0, dim - j - 1):
            row = dim - 1 - i
            col = j
            first_ri = row
            second_ri = row - 1
            a = mat[first_ri, col]
            b = mat[second_ri, col]
            et_mat = numpy.identity(dim)
            if b == 0:
                et_mat[:, [second_ri, first_ri]] = et_mat[:, [first_ri, second_ri]]
            else:
                k = -a / b

                et_mat[first_ri, second_ri] = k
            mat = numpy.matmul(et_mat, mat)
    return mat


def upward_elimination(mat: numpy.ndarray):
    dim = mat.shape[0]
    et_mat = numpy.identity(dim)
    for j in range(0, dim):
        et_mat[j, j] = 1 / mat[j, j]
    mat = numpy.matmul(et_mat, mat)
    for j in range(1, dim):
        for i in range(0, j):
            row = i
            col = j
            k = -mat[row, col]
            et_mat = numpy.identity(dim)
            et_mat[row, col] = k
            mat = numpy.matmul(et_mat, mat)
    return mat


def inverse_by_row_et(mat: numpy.ndarray):
    mat_inv = mat.copy()
    dim = mat_inv.shape[0]
    elem_mat = mat_proto(dim, dim)
    mat_inv = numpy.hstack((mat_inv, elem_mat))
    mat_inv = upper_tri_mat(mat_inv)
    mat_inv = upward_elimination(mat_inv)
    right_half = mat_inv[:, dim:2 * dim]
    return right_half


def calculate_cofactor(i, j, mat: numpy.ndarray):
    sign = (-1) ** (i + j + 2)
    cofactor_mat = mat.copy()
    cofactor_mat = numpy.delete(cofactor_mat, i, axis=0)
    cofactor_mat = numpy.delete(cofactor_mat, j, axis=1)
    cofactor = sign * numpy.linalg.det(cofactor_mat)
    return cofactor


def adjugate_by_cofactor(mat: numpy.ndarray):
    adj_mat = mat.copy()
    adj_mat = adj_mat.astype(numpy.float)
    dim = adj_mat.shape[0]
    for i in range(0, dim):
        for j in range(0, dim):
            adj_mat[i, j] = calculate_cofactor(i, j, mat)
    adj_mat = numpy.transpose(adj_mat)
    return adj_mat


def test_inv():
    matrix = mat_conditions(5, 1)
    matrix = matrix[list(matrix.keys())[0]]
    inv_matrix = inverse_by_row_et(matrix)
    inv_matrix_2 = numpy.linalg.inv(matrix)
    test1 = numpy.matmul(matrix, inv_matrix)
    test2 = numpy.matmul(inv_matrix, matrix)


if __name__ == '__main__':
    # test_mat = generate_mat_by_et()[1]
    test_mat = numpy.array([[1, 27, 6], [0, 9, 2], [0, 40, 9]])
    adj_matrix = adjugate_by_cofactor(test_mat)
    adj_matrix_2 = numpy.linalg.inv(test_mat) * numpy.linalg.det(test_mat)
    print('Done')
