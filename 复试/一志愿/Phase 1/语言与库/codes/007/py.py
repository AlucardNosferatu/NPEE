# 题目名称：字母异位词分组→unordered_map作为分组映射，vector存储结果列表
def group_anagrams(strs: list[str]) -> list[list[str]]:
    # 数据结构定义：使用字典将排序后的字符串作为键，原字符串列表作为值，对应C++ unordered_map<string, vector<string>>
    anagram_map = {}  # 键：排序后的字符串，值：原字符串列表，对应C++ unordered_map

    # 核心逻辑：遍历字符串列表，按排序后的字符串分组
    for s in strs:  # 遍历每个字符串，对应C++ vector<string>遍历
        # 操作目的：对字符串排序，将排序后的字符串作为分组键，对应STL的sort算法（需先转换为可排序结构）
        sorted_s = ''.join(sorted(s))  # 排序并重新拼接，对应C++ sort(s.begin(), s.end())得到排序后字符串
        
        # 判断条件：检查排序后的字符串是否已在映射中，对应STL的find方法
        if sorted_s not in anagram_map:  # 新分组键，对应unordered_map的find检查
            anagram_map[sorted_s] = []  # 初始化该键对应的列表，对应vector默认构造
        
        # 核心操作：将原字符串添加到对应分组的列表中，对应STL的push_back
        anagram_map[sorted_s].append(s)  # 加入分组，对应vector的push_back

    # 结果提取：将映射表的所有值转换为列表，对应C++ vector<vector<string>>构造
    result = list(anagram_map.values())  # 提取所有分组，对应遍历unordered_map并收集vector

    return result  # 返回分组结果，对应C++ vector<vector<string>>