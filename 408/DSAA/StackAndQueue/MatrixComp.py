import numpy


def gen_upper_tm(mat_dim=3, int_range_lb=-9, int_range_ub=9):
    mat_utm = numpy.random.randint(int_range_lb, int_range_ub, size=(mat_dim, mat_dim))
    mat_utm = numpy.triu(mat_utm, 0)
    return mat_utm


def gen_lower_tm(mat_dim=3, int_range_lb=-3, int_range_ub=3):
    mat_ltm = gen_upper_tm(mat_dim, int_range_lb, int_range_ub)
    mat_ltm = mat_ltm.T
    return mat_ltm


def mat_2_1darr(mat, row_major=True):
    arr1d = []
    if row_major:
        first_dim = mat.shape[0]
        second_dim = mat.shape[1]
    else:
        first_dim = mat.shape[1]
        second_dim = mat.shape[0]
    for i in range(0, first_dim):
        for j in range(0, second_dim):
            if row_major:
                arr1d.append(mat[i, j])
            else:
                arr1d.append(mat[j, i])
    return arr1d


def mat_tm_2_1darr(mat, utm=True, row_major=True):
    arr1d = []
    if row_major:
        first_dim = mat.shape[1]
        second_dim = mat.shape[0]
    else:
        first_dim = mat.shape[0]
        second_dim = mat.shape[1]
    for i in range(0, first_dim):
        if (utm and row_major) or (not utm and not row_major):
            second_range = range(i, second_dim)
        else:
            second_range = range(0, i + 1)
        for j in second_range:
            if row_major:
                arr1d.append(mat[i, j])
            else:
                arr1d.append(mat[j, i])
    return arr1d


def ai2mi(k=6, dim=4, utm=True, row_major=True):
    col = 1
    if utm ^ row_major:
        temp = col * (col + 1) / 2
        while temp < k:
            col += 1
            temp = col * (col + 1) / 2
        temp = col * (col - 1) / 2
        row = int(k - temp)
    else:
        temp = col * (2 * dim + 1 - col) / 2
        while temp < k:
            col += 1
            temp = col * (2 * dim + 1 - col) / 2
        temp = (col - 1) * (2 * dim + 2 - col) / 2
        row = int(k - temp) + col - 1
    if row_major:
        temp = row
        row = col
        col = temp
    return row, col


def mi2ai(row_i, col_j, dim, utm=True, row_major=True):
    # ri,cj start from 1
    # ai start from 1
    if (utm and col_j < row_i) or (not utm and col_j > row_i):
        return -1
        # means 0
    elif utm and not row_major:
        return (col_j * (col_j - 1) / 2) + row_i
    elif not utm and row_major:
        return (row_i * (row_i - 1) / 2) + col_j
    elif utm and row_major:
        row_base = dim - (row_i - 1)
        rows_base = 0
        for rb in range(row_base + 1, dim + 1):
            rows_base += rb
        col_shift = col_j - (row_i - 1)
        return rows_base + col_shift
    elif not utm and not row_major:
        col_base = dim - (col_j - 1)
        cols_base = 0
        for cb in range(col_base + 1, dim + 1):
            cols_base += cb
        row_shift = row_i - (col_j - 1)
        return cols_base + row_shift


def test_0():
    matrix_0 = gen_lower_tm()
    matrix_1 = gen_upper_tm()
    array_0_0 = mat_tm_2_1darr(matrix_0, utm=False, row_major=True)
    array_0_1 = mat_tm_2_1darr(matrix_0, utm=False, row_major=False)
    array_1_0 = mat_tm_2_1darr(matrix_1, utm=True, row_major=True)
    array_1_1 = mat_tm_2_1darr(matrix_1, utm=True, row_major=False)
    return [array_0_0, array_0_1, array_1_0, array_1_1]


if __name__ == '__main__':
    i11, j11 = ai2mi(k=7, utm=True, row_major=True)
    i12, j12 = ai2mi(k=6, utm=True, row_major=True)
    i13, j13 = ai2mi(k=8, utm=True, row_major=True)

    i21, j21 = ai2mi(k=6, utm=True, row_major=False)
    i22, j22 = ai2mi(k=5, utm=True, row_major=False)
    i23, j23 = ai2mi(k=7, utm=True, row_major=False)

    i31, j31 = ai2mi(k=6, utm=False, row_major=True)
    i32, j32 = ai2mi(k=5, utm=False, row_major=True)
    i33, j33 = ai2mi(k=7, utm=False, row_major=True)

    i41, j41 = ai2mi(k=7, utm=False, row_major=False)
    i42, j42 = ai2mi(k=6, utm=False, row_major=False)
    i43, j43 = ai2mi(k=8, utm=False, row_major=False)
    print('Done')
