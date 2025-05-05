import random

merge_count = 0


def shell_sort(input_list):
    gap = len(input_list) // 2
    while gap > 0:
        for i in range(gap, len(input_list)):
            tmp = input_list[i]
            j = i - gap
            while j >= 0 and tmp < input_list[j]:
                input_list[j + gap] = input_list[j]
                j -= gap
            input_list[j + gap] = tmp
        gap //= 2
    return input_list


def merge_sort(input_list):
    global merge_count
    if len(input_list) > 1:
        mid = len(input_list) // 2  # 使用整数除法确保分割对称
        left = merge_sort(input_list[:mid])
        right = merge_sort(input_list[mid:])
        input_list = merge_list(left, right)
        merge_count += 1  # 每次合并后正确计数
    return input_list


def merge_list(list_a, list_b):
    i, j = 0, 0
    merged_list = []
    while True:
        if list_a[i] < list_b[j]:
            merged_list.append(list_a[i])
            i += 1
        else:
            merged_list.append(list_b[j])
            j += 1
        if i >= len(list_a):
            while j < len(list_b):
                merged_list.append(list_b[j])
                j += 1
            break
        elif j >= len(list_b):
            while i < len(list_a):
                merged_list.append(list_a[i])
                i += 1
            break
    return merged_list


if __name__ == '__main__':
    a = list(range(1000))
    random.shuffle(a)
    print(a)
    print(shell_sort(input_list=a))
