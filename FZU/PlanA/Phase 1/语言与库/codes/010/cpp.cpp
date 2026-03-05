#include <vector>
#include <unordered_map>
using namespace std;
vector<int> next_greater_element(vector<int> &nums1, vector<int> &nums2)
{
    unordered_map<int, int> next_greater_map;
    vector<int> stack;
    for (const int &num : nums2)
    {
        while (!stack.empty() && stack.back() < num)
        {
            int smaller = stack.back();
            stack.pop_back();
            next_greater_map[smaller] = num;
        }
        stack.push_back(num);
    }
    while (!stack.empty())
    {
        int remaining = stack.back();
        stack.pop_back();
        next_greater_map[remaining] = -1;
    }
    vector<int> result;
    for (const int &num : nums1)
    {
        result.push_back(next_greater_map[num]);
    }
    return result;
}