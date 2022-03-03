a = {'data': 5, 'next': None}
a = {'data': 9, 'next': a}
a = {'data': 3, 'next': a}
a = {'data': 1, 'next': a}
a = {'data': 2, 'next': a}
a = {'data': 8, 'next': a}
a = {'data': 4, 'next': a}
a = {'data': 7, 'next': a}
a = {'data': 6, 'next': a}


def delete_x(l_dict, x):
    if l_dict['next'] is not None:
        l_dict['next'] = delete_x(l_dict['next'], x)
    if l_dict['data'] is x:
        l_dict = l_dict['next']
    return l_dict


def reverse_seq(l_dict):
    p = l_dict
    while p['next'] is not None:
        p = p['next']
    mover = l_dict
    last_mover = True
    while mover != p:
        l_dict = mover['next']
        if last_mover:
            mover['next'] = None
            last_mover = not last_mover
        if p['next'] is not None:
            mover['next'] = p['next']
        p['next'] = mover
        mover = l_dict
    return p


def nl_sort_pop_once(l_dict, prev_p=None):
    p = l_dict
    while p['next'] is not prev_p:
        first = p
        second = p['next']
        if first['data'] > second['data']:
            temp = first['data']
            first['data'] = second['data']
            second['data'] = temp
        p = p['next']
    return l_dict, p


def nl_sort_pop(l_dict):
    prev_p = None
    while prev_p is not l_dict:
        l_dict, prev_p = nl_sort_pop_once(l_dict, prev_p)
    return l_dict


a = nl_sort_pop(a)
print(a)
