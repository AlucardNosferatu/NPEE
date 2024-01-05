def hanoi(disks2move, from_column, via_column, to_column):
    if disks2move > 0:
        a, b, c = from_column, via_column, to_column
        hanoi(disks2move=disks2move - 1, from_column=a, via_column=c, to_column=b)
        print('move the top disk of {} to {}'.format(a, c))
        hanoi(disks2move=disks2move - 1, from_column=b, via_column=a, to_column=c)


if __name__ == '__main__':
    hanoi(disks2move=6, from_column='柱A', via_column='柱B', to_column='柱C')
