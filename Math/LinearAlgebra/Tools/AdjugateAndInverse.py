import numpy

from ElemTrans import mat_proto
from Matrix import mat_conditions


def is_invertible(mat):
    det = numpy.linalg.det(mat)
    return det != 0


def upper_tri_mat(mat):
    pass


def inverse_by_row_et(mat: numpy.ndarray):
    dim = mat.shape[0]
    elem_mat = mat_proto(dim, dim)
    mat = numpy.hstack((mat, elem_mat))
    for j in range(0, dim):
        for i in range(0, dim - j - 1):
            row = dim - 1 - i
            col = j
    pass


if __name__ == '__main__':
    mat = mat_conditions(5, 1)
    mat = mat[list(mat.keys())[0]]
    inverse_by_row_et(mat)
