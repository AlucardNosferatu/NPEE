import random

from MultiLayersCaches import CacheSys


def generate_cache_question():
    # 生成合理的主存和缓存参数（确保Nc < Nm, Tc < Tm）
    Nc = random.randint(2000, 10000) // 100 * 100  # 缓存访问次数
    Nm = random.randint(100, Nc // 2) // 100 * 100  # 主存访问次数
    Tm = random.randint(100, 300) // 10 * 10  # 主存访问时间（ns）
    Tc = random.randint(1, Tm - 1) // 10 * 10  # 缓存访问时间（必须小于Tm）

    mode = random.choice(['并行访存', '串行访存'])
    if mode == '串行访存':
        default_without_prompt = random.choice([True, False])
    elif mode == '并行访存':
        default_without_prompt = False
    else:
        raise ValueError('mode必须是“串行访存”或者“并行访存”')
    # 初始化条件字典
    conditions = {'Nc': Nc, 'Nm': Nm, 'Tc': Tc, 'Tm': Tm}

    # 调用CacheSys求解
    cs = CacheSys(mode=mode)

    Ef = cs.solve(cond=conditions, need='Ef')
    Rh = cs.solve(cond=conditions, need='Rh')
    Ta = cs.solve(cond=conditions, need='Ta')

    # 构造问题与答案
    mode_prompt = {False: f'主存访问模式为{mode}，', True: ''}
    question = (
        f"设缓存访问次数Nc={Nc}次，主存访问次数Nm={Nm}次，缓存访问时间Tc={Tc}ns，"
        f"主存访问时间Tm={Tm}ns，{mode_prompt[default_without_prompt]}请计算：\n"
        f"1. 命中率Rh\n2. 平均访问时间Ta\n3. 缓存效率Ef"
    )
    answer = (
        f"答案：\n"
        f"1. 命中率Rh = {float(Rh[1])}\n"
        f"2. 平均访问时间Ta = {float(Ta[1])}ns\n"
        f"3. 缓存效率Ef = {float(Ef[1])}"
    )
    return question, answer


if __name__ == '__main__':
    # 示例调用
    q, a = generate_cache_question()
    print("题目：\n" + q + "\n")
    print("解答：\n" + a)
