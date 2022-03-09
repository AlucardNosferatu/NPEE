import numpy
import datetime
from AdjugateAndInverse import upper_tri_mat
from ElemTrans import generate_mat_by_et


def enumerate_nz_sd(mat, utm=False):
    queue = [mat]
    while len(queue) > 0:
        sub_mat = queue.pop(0)
        if numpy.linalg.det(sub_mat) != 0:
            return sub_mat.shape[0]
        else:
            if utm:
                new_mat = numpy.delete(sub_mat, sub_mat.shape[0] - 1, axis=0)
                new_mat = numpy.delete(new_mat, 0, axis=1)
                queue.append(new_mat)
            else:
                for i in range(0, sub_mat.shape[0]):
                    for j in range(0, sub_mat.shape[0]):
                        new_mat = numpy.delete(sub_mat, i, axis=0)
                        new_mat = numpy.delete(new_mat, j, axis=1)
                        queue.append(new_mat)
    return 0


def row_reduce(mat):
    mat_reduced = upper_tri_mat(mat, True)
    rank = enumerate_nz_sd(mat_reduced, True)
    return rank


if __name__ == '__main__':
    mat_proto, test_mat = generate_mat_by_et(dim=5, et_count=10, rank=4)
    # test_mat = numpy.array(
    #     [
    #         [0, 1, 0, 0, 0],
    #         [11, 0, 1, 0, 0],
    #         [0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 3],
    #         [0, 0, 0, 2, 0]
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
