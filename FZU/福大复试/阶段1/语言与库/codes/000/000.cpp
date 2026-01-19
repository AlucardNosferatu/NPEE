#include <vector>
#include <utility>
#include <unordered_map>

using namespace std;
vector<int> two_sum_indices(vector<int> nums, int target)
{
    vector<int> res;
    res.clear();
    unordered_map<int, int> index_map;
    int complement;
    for (int i = 0; i < nums.size(); i++)
    {
        complement = target - nums[i];
        if (index_map.count(complement) > 0)
        {
            res.push_back(index_map[complement]);
            res.push_back(i);
            return res;
        }
        index_map[nums[i]] = i;
    }
    return res;
}