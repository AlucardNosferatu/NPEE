import random

problems_types = [
    'exec_t',
    'freq',
    'cpi',
    'mips',
    'ins_count',
    'ins_occ',
    'ins_cpi'
]
q_text = {
    'exec_t': '请算出对应的执行用时',
    'freq': '请算出CPU主频'
}
c_text = {
    'exec_t': '执行用时为',
    'freq': 'CPU主频为',
    'cpi': '总体CPI为',
    'mips': '每秒执行百万次指令倍数（MIPS）为',
    'ins_count': '基准程序指令条数为',
    'ins_occ': '几种指令在基准程序出现的次数为',
    'ins_cpi': '几种指令分别的CPI为'
}


def ins_specified_cpi(n):
    ins_cpi = []
    ins_occurrence = []
    for i in range(0, n):
        ins_cpi.append(random.randint(1, 4))
        ins_occurrence.append(random.randint(2, 10))
    return ins_cpi, ins_occurrence


def general_cpi(ins_cpi, ins_occurrence):
    total_occ = sum(ins_occurrence)
    total_cpi = []
    for i in range(0, len(ins_cpi)):
        total_cpi.append(ins_cpi[i] * ins_occurrence[i])
    total_cpi = sum(total_cpi)
    g_cpi = total_cpi / total_occ
    return g_cpi, g_cpi.is_integer()


def freq():
    freq_mantissa = random.randint(1, 10)
    freq_exponent = random.randint(3, 6)
    return freq_mantissa, freq_exponent


def mips_cal(freq_man, freq_exp, cpi):
    while freq_exp != 6:
        if freq_exp > 6:
            freq_man *= 10
            freq_exp -= 1
        elif freq_exp < 6:
            freq_man /= 10
            freq_exp += 1
        else:
            print('Error!')
    mips = freq_man / cpi
    return mips


def exec_time(ins_count, cpi, freq_man, freq_exp):
    while freq_exp != 6:
        if freq_exp > 6:
            freq_man *= 10
            freq_exp -= 1
        elif freq_exp < 6:
            freq_man /= 10
            freq_exp += 1
        else:
            print('Error!')
    exec_t_man = ins_count * cpi / freq_man
    exec_t_exp = -freq_exp
    return exec_t_man, exec_t_exp


def replace_last_cpi(icpi, iocc, gcpi):
    changed = 0
    for i in range(0, len(icpi) - 1):
        changed += ((gcpi - icpi[i]) * iocc[i])
    iocc[-1] = 11
    rem = -1
    while rem != 0:
        iocc[-1] -= 1
        temp = changed + gcpi * iocc[-1]
        rem = temp % iocc[-1]
    icpi[-1] = int((changed / iocc[-1]) + gcpi)
    return icpi, iocc


def conditions_gen(specify_mips=True, int_gcpi=True, specify_ins_types_count=None):
    conditions = {}
    if specify_ins_types_count is None:
        ins_types_count = random.randint(2, 4)
    else:
        ins_types_count = specify_ins_types_count
    icpi, iocc = ins_specified_cpi(ins_types_count)
    gcpi, is_int = general_cpi(icpi, iocc)
    if not is_int and int_gcpi:
        gcpi = max(icpi)
        # gcpi = random.randint(max_cpi, max_cpi + 5)
        # todo:lower gcpi
        icpi, iocc = replace_last_cpi(icpi, iocc, gcpi)
    conditions['ins_occ'] = iocc
    conditions['ins_cpi'] = icpi
    conditions['cpi'] = gcpi
    if specify_mips:
        mips = random.randint(1, 10)
        freq_exp = 6
        freq_man = gcpi * mips
    else:
        freq_man, freq_exp = freq()
        mips = mips_cal(freq_man, freq_exp, gcpi)
    conditions['freq'] = [freq_man, freq_exp]
    conditions['mips'] = mips
    ins_count = random.randint(10, 100)
    conditions['ins_count'] = ins_count
    et_man, et_exp = exec_time(ins_count, gcpi, freq_man, freq_exp)
    conditions['exec_t'] = [et_man, et_exp]
    return conditions


def problems_gen():
    all_conditions = conditions_gen()
    revealed_conditions = {}
    req_conditions = []
    p_type = random.choice(problems_types)
    p_type = 'freq'
    answer = all_conditions[p_type]
    if p_type == 'exec_t':
        req_conditions = ['ins_count', 'freq', 'ins_occ', 'ins_cpi']
    elif p_type == 'freq':
        rc_1 = ['mips', 'ins_occ', 'ins_cpi']
        rc_2 = ['exec_t', 'ins_count', 'cpi']
        req_conditions = random.choice([rc_1, rc_2])
    for rc in req_conditions:
        revealed_conditions[rc] = all_conditions[rc]
    return revealed_conditions, answer, p_type, all_conditions


def interaction():
    rc, ans, pt, ac = problems_gen()
    while True:
        print('已知：')
        for key in rc:
            if key in ['freq', 'exec_t']:
                print(c_text[key], rc[key][0], '*(10^', rc[key][1], ')')
            else:
                print(c_text[key], rc[key])
        print(q_text[pt])
        answer = input('（若输入浮点数请用“,”分隔尾数和阶数）')
        if answer is 'fuck':
            print('答案是：', ans)
        elif answer is 'skip':
            print('跳过本题。。。')
            break
        elif ',' in answer:
            answer = answer.split(',')
            answer = float(answer[0]) * (10 ** int(answer[1]))
            diff = abs(answer - ans[0] * (10 ** ans[1]))
            diff /= (10 ** 6)
            if diff < 0.01:
                print('Correct!')
                break
            else:
                print('Wrong!')


if __name__ == '__main__':
    while True:
        interaction()
