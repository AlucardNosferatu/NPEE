#include <vector>
#include <unordered_map>
using namespace std;
int subarray_sum_equals_k(vector<int> &nums, int k)
{
    unordered_map<int, int> prefix_sum_map;
    prefix_sum_map[0] = 1;
    int current_sum = 0;
    int count = 0;
    for (const int &num : nums)
    {
        current_sum = current_sum + num;
        int target = current_sum - k;
        if (prefix_sum_map.count(target))
        {
            count += prefix_sum_map[target];
        }
        prefix_sum_map[current_sum] = prefix_sum_map[current_sum] + 1;
    }
    return count;
}