import random


def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)


def combination(n, m):
    if n < m:
        n = n + m
        m = n - m
        n = n - m
    return factorial(n) / (factorial(m) * factorial(n - m))


def catalan_number(n):
    return combination(2 * n, n) / (n + 1)


def cn_problems():
    n = random.randint(3, 10)
    cn = catalan_number(n)
    while True:
        print(n, '个不同元素进栈，请问有多少种出栈顺序？')
        answer = input()
        if answer == str(int(cn)):
            print('Correct! The answers is:', cn)
            break
        elif answer == 'fuck':
            print('The answers is:', cn)
        elif answer == 'skip':
            print('Skipped.')
            break


def st_insert_and_delete(length, n):
    assert n <= length
    return length - n


def stid_problems():
    length = random.randint(100, 1000)
    n = random.randint(1, length)
    mc = st_insert_and_delete(length, n)
    while True:
        print('对长度为', length, '的顺序表其中第', n, '个元素做增删操作，需要移动多少个元素？')
        answer = input()
        if answer == str(int(mc)):
            print('Correct! The answers is:', mc)
            break
        elif answer == 'fuck':
            print('The answers is:', mc)
        elif answer == 'skip':
            print('Skipped.')
            break


def stack_manipulation_tree(input_seq, stack, output_seq, m='app'):
    root = {}
    node_is = input_seq.copy()
    node_stack = stack.copy()
    node_os = output_seq.copy()
    if m == 'app':
        if len(node_is) > 0:
            node_stack.append(node_is.pop(0))
            root['s'] = node_stack
            root['os'] = node_os
        else:
            return None
    else:
        if len(node_stack) > 0:
            node_os.append(node_stack.pop(-1))
            root['s'] = node_stack
            root['os'] = node_os
        else:
            return None
    root['app'] = stack_manipulation_tree(node_is, node_stack, node_os, 'app')
    root['pop'] = stack_manipulation_tree(node_is, node_stack, node_os, 'pop')
    return root


def tree_printer(stack_tree, lines=None, depth=0):
    if stack_tree is not None:
        if lines is None:
            lines = []
        while len(lines) <= depth:
            lines.append([])
        lines[depth].append({'s': stack_tree['s'], 'os': stack_tree['os']})
        if 'app' in stack_tree:
            tree_printer(stack_tree['app'], lines, depth=depth + 1)
        if 'pop' in stack_tree:
            tree_printer(stack_tree['pop'], lines, depth=depth + 1)
    return lines


def test_st():
    st = stack_manipulation_tree([1, 2, 3, 4, 5, 6], [], [])
    st_lines = tree_printer(st)
    print(len(st_lines[-1]))


def cq_empty_or_full(max_size, front_pos, rear_pos, last_op=None):
    if last_op is None:
        if front_pos == rear_pos:
            return 0
        elif (rear_pos + 1) % max_size == front_pos:
            return max_size
        else:
            return (rear_pos + max_size - front_pos) % max_size
    elif front_pos == rear_pos:
        if last_op == 'delete':
            return 0
        elif last_op == 'insert':
            return max_size
        else:
            return -1
    else:
        return (rear_pos + max_size - front_pos) % max_size


