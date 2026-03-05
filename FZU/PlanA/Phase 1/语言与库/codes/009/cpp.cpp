#include <vector>
#include <unordered_map>
using namespace std;
vector<int> intersect(vector<int> &nums1, vector<int> &nums2)
{
    unordered_map<int, int> freq_map;
    for (int &num : nums1)
    {
        freq_map[num] = freq_map[num] + 1;
    }
    vector<int> result;
    for (int &num : nums2)
    {
        if (freq_map.count(num) && freq_map[num] > 0)
        {
            result.push_back(num);
            freq_map[num] = freq_map[num] - 1;
        }
    }
    return result;
}