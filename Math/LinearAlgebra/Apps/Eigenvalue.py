import numpy


def eigenvalue():
    flag = True
    mat_rows = numpy.zeros(shape=(3, 3))
    while flag:
        print('输入矩阵，以;分隔行，以,分隔列，例如：')
        print('1 2 3')
        print('4 5 6')
        print('7 8 9')
        print('上述矩阵写作：1,2,3;4,5,6;7,8,9')
        print('确保矩阵是n*n否则可能报错或崩溃')
        mat_str = input()
        mat_rows = mat_str.split(';')
        mat_rows = [row.split(',') for row in mat_rows]
        mat_rows = [[int(element) for element in row] for row in mat_rows]
        mat_rows = numpy.array(mat_rows)
        while True:
            print('矩阵为：')
            print(mat_rows)
            print('y/n')
            yes = input()
            if yes == 'y':
                flag = False
                break
            elif yes == 'n':
                break
            else:
                print('提示：输入y确认，输入n重输')
    print('开始计算特征值。。。')
    ev = numpy.linalg.eigvals(mat_rows)
    ev = ev.tolist()
    # noinspection PyTypeChecker
    ev = [int(numpy.round(element)) for element in ev]
    print('特征值为：')
    print(ev)
    return ev


if __name__ == '__main__':
    while True:
        eigenvalue()
        print()
        print()
        print()
