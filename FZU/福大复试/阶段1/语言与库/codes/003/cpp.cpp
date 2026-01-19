#include <vector>
#include <unordered_map>
#include <algorithm>
using namespace std;

bool a_before_b(const pair<int, int> &a, const pair<int, int> &b)
{
    return a.second > b.second;
}

vector<int> top_k_frequent(vector<int> nums, int k)
{
    unordered_map<int, int> freq_map;
    for (const int &num : nums)
    {
        freq_map[num] = freq_map[num] + 1;
        // cpp的map默认初始化0
    }
    vector<pair<int, int>> items;
    for (const auto &kv : freq_map)
    {
        items.push_back(kv); // 提取键值对
    }
    vector<pair<int, int>> sorted_items = items;
    sort(sorted_items.begin(), sorted_items.end(), a_before_b); // 传入自定义函数
    vector<int> result;
    for (int i = 0; i < min((int)sorted_items.size(), k); i++)
    {
        result.push_back(sorted_items[i].first);
    }
    return result;
}