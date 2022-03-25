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

        # region 化行最简
        sol_mat = non_zero_diagonal(aug_mat)
        sol_mat = upper_tri_mat(mat=sol_mat)
        sol_mat = upward_elimination(sol_mat)
        # endregion

        # region 确定约束变量位置
        x_template = []
        x_list = []
        const_var_list = []
        for i in range(0, sol_mat.shape[0]):
            if sol_mat[i, 0:cv_count].any():
                const_var = sol_mat[i, 0:cv_count] != 0
                const_var = const_var.argmax(axis=0)
                const_var_list.append(const_var)
        # endregion

        # region 构造自由变量全0向量（非齐次特解）
        for i in range(0, cv_count):
            if i in const_var_list:
                x_template.append(-1)
            else:
                x_template.append(0)
        x_list.append(x_template)
        # endregion

        # region 构造自由变量独热码（基础解系）
        for i in range(0, cv_count):
            if i not in const_var_list:
                x_list.append(x_template.copy())
                x_list[-1][i] = 1
        # endregion

        # region 代入x取值求出非齐次特解和基础解系
        basic_sol_sys = []
        nss = True
        for x_bss in x_list:
            smb = sol_mat.copy()
            if not nss:
                # 求基础解系，同系数阵的齐次方程组（Ax=0）常数列变0
                smb[:, -1] = smb[:, -1] - smb[:, -1]
            else:
                # 非齐次特解，保留非0常数列（Ax=b）
                pass
            nss = False
            # 只有第一次代入是求非齐次特解
            shift = 0
            for i in range(0, cv_count):
                # -1代表约束变量，所在列不会动
                if x_bss[i] != -1:
                    if x_bss[i] == 1:
                        # 自由变量为1，从常数列减去自由变量所在列
                        smb[:, -1] = smb[:, -1] - smb[:, i + shift]
                    else:
                        # 自由变量为0，不改变常数列
                        pass
                    # 从系数阵里删去自由变量列（物理消元）
                    smb = numpy.delete(smb, i + shift, axis=1)
                    shift -= 1
            sol_vec = []
            # 求出约束变量取值，打包解向量
            for i in range(0, cv_count):
                if i in const_var_list:
                    # 约束变量此时系数为1（前面化行最简确保）
                    # 可直接取对应行常数列的值
                    sol_vec.append(smb[i, -1])
                else:
                    # 自由变量取值以独热码设定为准
                    sol_vec.append(x_bss[i])
            sol_vec = numpy.array([sol_vec]).T
            basic_sol_sys.append(sol_vec)
        # endregion

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


def vec_operation(conditions, question):
    question_str = str(question)
    for i in range(1, len(question)):
        if type(question[i]) == list:
            question[i], qs = vec_operation(conditions, question[i])
        if type(question[i]) is int:
            question[i] = conditions[question[i]].copy()
        try:
            if i != 1:
                if question[0] == '*':
                    question[1] = numpy.dot(question[1], question[i])
                elif question[0] == '+':
                    question[1] += question[i]
                elif question[0] == '×':
                    question[1] = numpy.cross(question[1], question[i])
            elif question[0] == 'mag':
                question[i] = numpy.linalg.norm(question[i])
            elif question[0] == 'uni':
                question[i] = question[i] / numpy.linalg.norm(question[i])
        except Exception as e:
            return e, question_str
    return question[1], question_str


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
    vec_cond = gen_vectors(dim=3, count=4, rank=3)
    vec_res = vec_operation(conditions=vec_cond, question=['*', ['+', 0, 1], ['×', 2, 3]])
    print('Done')
