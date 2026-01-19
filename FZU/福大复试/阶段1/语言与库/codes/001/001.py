# 题目名称：字符串第一个唯一字符查找→unordered_map频次统计，string遍历
def first_unique_char(s: str) -> int:
    # 数据结构定义：使用字典统计字符出现频次，对应C++ unordered_map<char, int>
    freq_map = {}  # 键：字符，值：出现次数，对应C++ unordered_map

    # 核心逻辑1：首次遍历统计每个字符频次，对应STL的[]运算符或insert操作
    for ch in s:  # 遍历字符串字符，对应C++ string的迭代器或下标访问
        # 操作目的：新增或更新字符频次，对应STL的[]运算符（若键不存在则自动插入）
        freq_map[ch] = freq_map.get(ch, 0) + 1  # 获取当前频次并加1，对应STL的find+[]组合操作

    # 核心逻辑2：第二次遍历查找第一个频次为1的字符索引，对应vector/list的索引遍历
    for idx, ch in enumerate(s):  # 同时获取索引和字符，对应C++ string下标遍历
        # 判断条件：检查当前字符频次是否为1，对应STL的find查找或[]访问
        if freq_map[ch] == 1:  # 字符频次为1表示唯一，对应unordered_map的键值访问
            return idx  # 返回第一个满足条件的索引，对应C++ int类型返回

    # 边界处理：若没有唯一字符，返回-1（标准约定），对应C++返回-1
    return -1  # 无唯一字符，返回固定值-1