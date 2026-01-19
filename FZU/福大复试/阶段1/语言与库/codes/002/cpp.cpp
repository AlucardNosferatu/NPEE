#include <vector>
#include <algorithm>

using namespace std;

bool a_before_b(const vector<int> &a, const vector<int> &b)
{
    return a[0] < b[0];
}

vector<vector<int>> merge_intervals(vector<vector<int>> intervals)
{
    vector<vector<int>> merged;
    vector<vector<int>> sorted_intervals = intervals;

    sort(sorted_intervals.begin(), sorted_intervals.end(), a_before_b); // 传入自定义函数

    vector<int> temp;
    int start, end;
    for (const vector<int> &interval : sorted_intervals)
    {
        start = interval[0];
        end = interval[1];
        if (merged.empty() || merged.back()[1] < start)
        {
            merged.push_back(vector<int>{start, end});
        }
        else
        {
            merged.back()[1] = max(merged[merged.size() - 1][1], end);
        }
    }
    return merged;
}