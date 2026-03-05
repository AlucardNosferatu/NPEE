#include <vector>
#include <string>
#include <unordered_map>
#include <algorithm>
using namespace std;
vector<vector<string>> group_anagrams(vector<string> strs)
{
    unordered_map<string, vector<string>> anagram_map;
    string sorted_s;
    for (string &s : strs)
    {
        sorted_s = s;
        sort(sorted_s.begin(), sorted_s.end());
        if (anagram_map.count(sorted_s) <= 0)
        {
            anagram_map[sorted_s] = vector<string>();
        }
        anagram_map[sorted_s].push_back(s);
    }
    vector<vector<string>> result; // C++ vector 对应 Python list
    // 范围 for 遍历：忽略 key（pair.first），只提取 value（pair.second）
    for (const auto &key_value_pair : anagram_map)
    {
        // 存入 value，完成转换（等价于 Python list() 构造）
        result.push_back(key_value_pair.second);
    }
    return result;
}