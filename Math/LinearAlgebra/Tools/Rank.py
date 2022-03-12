import numpy
import datetime
from AdjugateAndInverse import upper_tri_mat, non_zero_diagonal
from ElemTrans import generate_mat_by_et


def enumerate_nz_sd(mat):
    queue = [mat]
    while len(queue) > 0:
        sub_mat = queue.pop(0)
        if numpy.linalg.det(sub_mat) != 0:
            return sub_mat.shape[0]
        else:
            for i in range(0, sub_mat.shape[0]):
                for j in range(0, sub_mat.shape[0]):
                    new_mat = numpy.delete(sub_mat, i, axis=0)
                    new_mat = numpy.delete(new_mat, j, axis=1)
                    queue.append(new_mat)
    return 0


def row_reduce(mat):
    mat_reduced = non_zero_diagonal(mat)
    mat_reduced = upper_tri_mat(mat_reduced)
    rank = mat_reduced.shape[0]
    for i in range(0, mat_reduced.shape[0]):
        if not mat_reduced[i, :].any():
            rank -= 1
    return rank


def test_rank():
    mat_proto, test_mat = generate_mat_by_et(dim=5, et_count=10, rank=4)
    # test_mat = numpy.array(
    #     [
    #         [108, 0, 0, 0, 0],
    #         [0, 3, 0, 0, 0],
    #         [0, 0, 0, 1, 0],
    #         [0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 1]
    #     ]
    # )
    s1 = datetime.datetime.now()
    r1 = enumerate_nz_sd(test_mat)
    e1 = datetime.datetime.now()
    s2 = datetime.datetime.now()
    r2 = row_reduce(test_mat)
    e2 = datetime.datetime.now()
    print(r1, r2)
    print(e1 - s1)
    print(e2 - s2)


if __name__ == '__main__':
    print('Done')
