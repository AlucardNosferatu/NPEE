import numpy

from AdjugateAndInverse import upper_tri_mat, non_zero_diagonal, upward_elimination
from ElemTrans import generate_mat_by_et


def gen_row_vec(dim=3, int_range_lb=-9, int_range_ub=9):
    vec = numpy.random.randint(int_range_lb, int_range_ub, size=(1, dim))
    return vec


def gen_col_vec(dim=3, int_range_lb=-9, int_range_ub=9):
    vec = numpy.random.randint(int_range_lb, int_range_ub, size=(dim, 1))
    return vec


def gen_vectors(dim=3, count=3, rank=3, et_count=5, col=True):
    vectors_list = []
    if rank > dim:
        print('Fuck, Dim cannot be lower than Rank!')
        dim = rank
    if rank > count:
        print('Fuck, Amount of vectors cannot be lower than Rank!')
        count = rank
    mat_count = int(count / dim) + 1
    for i in range(0, mat_count):
        _, mat = generate_mat_by_et(dim=dim, et_count=et_count, rank=rank)
        for j in range(0, mat.shape[1]):
            if col:
                vectors_list.append(mat[:, j].T)
            else:
                vectors_list.append(mat[:, j])
    return vectors_list[:count]


def vec_group_is_linear_correlative(vec_group):
    vec_count = len(vec_group)
    mat = numpy.stack(vec_group, axis=1).squeeze()
    if numpy.linalg.matrix_rank(mat) < vec_count:
        return True
    else:
        return False


def vec_can_be_rep_by_vec_group(vec, vec_group):
    cv_count = len(vec_group)
    coe_mat = numpy.stack(vec_group, axis=1).squeeze()
    aug_mat = numpy.hstack((coe_mat, vec))
    cmr = numpy.linalg.matrix_rank(coe_mat)
    amr = numpy.linalg.matrix_rank(aug_mat)
    if cmr < amr:
        print('系数阵的秩小于增广矩阵的秩')
        print('方程组无解')
        print('非齐次项向量不可由系数向量组线性表示。')
        return False, None
    elif cmr == amr == cv_count:
        print('系数阵的秩等于增广矩阵的秩等于系数向量个数')
        print('方程组有唯一解')
        print('非齐次项向量可由系数向量组线性表示。')
        sol_mat = non_zero_diagonal(aug_mat)
        sol_mat = upper_tri_mat(mat=sol_mat)
        sol_mat = upward_elimination(sol_mat)
        return True, sol_mat[:, -1]
    elif cmr == amr < cv_count:
        print('系数阵的秩等于增广矩阵的秩小于系数向量个数')
        print('方程组有无穷多解')
        print('非齐次项向量可由系数向量组线性表示，且表达式不唯一。')
        sol_mat = non_zero_diagonal(aug_mat)
        sol_mat = upper_tri_mat(mat=sol_mat)
        sol_mat = upward_elimination(sol_mat)
        x_template = []
        x_list = []
        const_var_list = []
        for i in range(0, sol_mat.shape[0]):
            if sol_mat[i, 0:cv_count].any():
                const_var = sol_mat[i, 0:cv_count] != 0
                const_var = const_var.argmax(axis=0)
                const_var_list.append(const_var)
        for i in range(0, cv_count):
            if i in const_var_list:
                x_template.append(-1)
            else:
                x_template.append(0)
        x_list.append(x_template)
        for i in range(0, cv_count):
            if i not in const_var_list:
                x_list.append(x_template.copy())
                x_list[-1][i] = 1
        basic_sol_sys = []
        nhs = True
        for x_bss in x_list:
            smb = sol_mat.copy()
            if not nhs:
                smb[:, -1] = smb[:, -1] - smb[:, -1]
            nhs = False
            shift = 0
            for i in range(0, cv_count):
                if x_bss[i] != -1:
                    if x_bss[i] == 1:
                        smb[:, -1] = smb[:, -1] - smb[:, i + shift]
                    smb = numpy.delete(smb, i + shift, axis=1)
                    shift -= 1
            sol_vec = []
            for i in range(0, cv_count):
                if i in const_var_list:
                    sol_vec.append(smb[i, -1])
                else:
                    sol_vec.append(x_bss[i])
            sol_vec = numpy.array([sol_vec]).T
            basic_sol_sys.append(sol_vec)
        return True, basic_sol_sys
    else:
        print('输入参数错误！')
        return False, None


def vec_group_can_be_rep_by_vec_group(vec_group_1, vec_group_2):
    how_to_rep_list = []
    can_be_rep_list = []
    for vector in vec_group_1:
        can_be_rep, how_to_rep = vec_can_be_rep_by_vec_group(vector, vec_group_2)
        how_to_rep_list.append(how_to_rep)
        can_be_rep_list.append(can_be_rep)
    conclusion = False not in can_be_rep_list
    return conclusion, can_be_rep_list, how_to_rep_list


def vec_groups_are_equivalent(vec_group_1, vec_group_2):
    conclusion_1, cl_1, hl_1 = vec_group_can_be_rep_by_vec_group(vec_group_1, vec_group_2)
    conclusion_2, cl_2, hl_2 = vec_group_can_be_rep_by_vec_group(vec_group_2, vec_group_1)
    return conclusion_1 and conclusion_2, [[cl_1, hl_1], [cl_2, hl_2]]


def test_1():
    # vl1 = gen_vectors(dim=3, count=4, rank=3)
    # vl2 = gen_vectors(dim=3, count=2, rank=3)
    # vl3 = gen_vectors(dim=3, count=3, rank=4)
    # v1 = gen_col_vec(dim=3)
    # v2 = numpy.array([[0, 0, 0]]).T
    vl2 = [
        numpy.array([[1, 0]]).T,
        numpy.array([[0, 1]]).T
    ]
    vl3 = [
        numpy.array([[1, 2]]).T,
        numpy.array([[1, 1]]).T,
        numpy.array([[2, 2]]).T
    ]
    # res1 = vec_can_be_rep_by_vectors(v2, vl2)
    res2 = vec_groups_are_equivalent(vl2, vl3)
    return res2


def test_2():
    vl1 = [
        numpy.array([[1, 2]]).T,
        numpy.array([[2, 3]]).T
    ]
    vl2 = [
        numpy.array([[1, 2]]).T,
        numpy.array([[2, 3]]).T,
        numpy.array([[1, 1]]).T
    ]
    vl3 = [
        numpy.array([[2, 1, 1]]).T,
        numpy.array([[1, 2, -1]]).T,
        numpy.array([[1, -1, 2]]).T
    ]
    vl4 = [
        numpy.array([[5, 1, 1]]).T,
        numpy.array([[1, 5, -1]]).T,
        numpy.array([[1, -1, 5]]).T
    ]
    vl5 = [
        numpy.array([[1, 2, -2, 1]]).T,
        numpy.array([[0, 1, -2, 1]]).T,
        numpy.array([[2, 1, 2, -1]]).T
    ]
    vl6 = [
        numpy.array([[1, 2, -2, 1]]).T,
        numpy.array([[0, 1, 7, 1]]).T,
        numpy.array([[2, 1, 2, -1]]).T
    ]
    res1 = vec_group_is_linear_correlative(vl1)
    res2 = vec_group_is_linear_correlative(vl2)
    res3 = vec_group_is_linear_correlative(vl3)
    res4 = vec_group_is_linear_correlative(vl4)
    res5 = vec_group_is_linear_correlative(vl5)
    res6 = vec_group_is_linear_correlative(vl6)
    return [res1, res2, res3, res4, res5, res6]


if __name__ == '__main__':
    print('Done')
