import random

from Profile import conditions_gen, general_cpi

text_cond = {
    'ins_cpi': '各指令CPI：',
    'ins_rat': '各指令占比：',
    'cause_index': '被优化的指令（list下标）：',
    'cause_change_rat': '被优化而减少的比例（相对指令自身）：',
    'result_indices': '受影响而等量减少的指令（list下标，包含被优化的指令）：'
}


def before_change(ins_types_count):
    all_conditions = conditions_gen(int_gcpi=False, specify_ins_types_count=ins_types_count)

    ins_ratio = []
    for ins_occ in all_conditions['ins_occ']:
        ins_ratio.append(ins_occ / sum(all_conditions['ins_occ']))
    origin_cond = {
        'ins_occ': all_conditions['ins_occ'],
        'ins_cpi': all_conditions['ins_cpi'],
        'cpi': all_conditions['cpi'],
        'total_occ': sum(all_conditions['ins_occ']),
        'ins_rat': ins_ratio
    }
    return origin_cond


def after_change(origin_cond):
    affected_count = random.randint(1, len(origin_cond['ins_cpi']))
    result_indices = []
    for i in range(0, affected_count):
        result_indices.append(random.randint(0, len(origin_cond['ins_cpi']) - 1))
    result_indices = list(set(result_indices))
    cause_index = random.choice(result_indices)
    result_ins_occ = origin_cond["ins_occ"].copy()
    cause_change_occ = random.randint(1, result_ins_occ[cause_index])
    cause_change_rat = cause_change_occ / result_ins_occ[cause_index]
    result_ins_occ[cause_index] -= cause_change_occ
    for index in result_indices:
        if index is not cause_index:
            result_ins_occ[index] = max(0, result_ins_occ[index] - cause_change_occ)
    result_ins_occ.append(cause_change_occ)
    result_ins_cpi = origin_cond['ins_cpi'].copy()
    result_ins_cpi.append(random.randint(1, 4))
    changed_cond = {
        'cause_index': cause_index,
        'cause_change_occ': cause_change_occ,
        'cause_change_rat': cause_change_rat,
        'result_indices': result_indices,
        'ins_occ': result_ins_occ,
        'ins_cpi': result_ins_cpi,
        'cpi': general_cpi(result_ins_cpi, result_ins_occ)[0]
    }
    return changed_cond


def shifted_cpi(ins_types_count):
    origin_cond = before_change(ins_types_count)
    changed_cond = after_change(origin_cond)
    req_cond = [
        [
            'ins_cpi',
            'ins_rat'
        ],
        [
            'ins_cpi',
            'cause_index',
            'cause_change_rat',
            'result_indices'
        ]
    ]
    answer = [origin_cond['cpi'], changed_cond['cpi']]
    return [origin_cond, changed_cond], req_cond, answer


def interaction():
    cond, req_cond, ans = shifted_cpi(4)
    cond_hint = ['指令系统改变前：', '指令系统改变后（新指令在list末尾）：']
    for i in range(0, 2):
        print(cond_hint[i])
        for cond_tag in req_cond[i]:
            print(text_cond[cond_tag], cond[i][cond_tag])
    print('请求出指令系统改变前后的平均CPI')
    print('答案：', ans)


if __name__ == '__main__':
    interaction()
