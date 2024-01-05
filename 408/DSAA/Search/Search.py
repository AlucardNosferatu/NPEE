import cProfile
import pstats
import random
import time
from math import floor


def linear_search(seq, target):
    for i in range(len(seq)):
        if seq[i] == target:
            return i
    return None


def binary_search(seq, target, low, high):
    if low > high:
        return -1
    mid = (low + high) // 2
    if seq[mid] == target:
        return mid
    elif seq[mid] < target:
        return binary_search(seq, target, mid + 1, high)
    else:
        return binary_search(seq, target, low, mid - 1)


def bs_test():
    seq = []
    p_scale = 10000
    for _ in range(p_scale):
        item = random.randint(a=-1 * p_scale, b=p_scale)
        while item in seq:
            item = random.randint(a=-1 * p_scale, b=p_scale)
        seq.append(item)
    target = random.choice([random.randint(a=-2 * p_scale, b=2 * p_scale), random.choice(seq)])
    profiler1 = cProfile.Profile()
    profiler2 = cProfile.Profile()
    now = time.time()
    profiler1.enable()
    res1 = binary_search(seq=seq, target=target, low=0, high=len(seq) - 1)
    profiler1.disable()
    spent1 = time.time() - now
    pstats.Stats(
        profiler1, stream=open('性能分析-二分查找.txt', 'a')
    ).sort_stats(pstats.SortKey.CUMULATIVE).print_stats()
    now = time.time()
    profiler2.enable()
    res2 = linear_search(seq=seq, target=target)
    profiler2.disable()
    spent2 = time.time() - now
    pstats.Stats(
        profiler2, stream=open('性能分析-线性查找.txt', 'a')
    ).sort_stats(pstats.SortKey.CUMULATIVE).print_stats()
    spend_d = spent2 - spent1
    return res1 == res2, spent1, spent2, spend_d


if __name__ == '__main__':
    all_c = []
    all_sd = []
    for _ in range(100):
        c, s1, s2, sd = bs_test()
        all_c.append(c)
        all_sd.append(sd)
        print(sum(all_sd), sum(all_sd) / len(all_sd))
