#include <vector>
#include <algorithm>
using namespace std;
int assign_cookies(vector<int> &g, vector<int> &s)
{
    sort(g.begin(), g.end());
    sort(s.begin(), s.end());
    int child_idx = 0;
    int cookie_idx = 0;
    while (child_idx < g.size() && cookie_idx < s.size())
    {
        if (s[cookie_idx] >= g[child_idx])
            child_idx++;
        cookie_idx++;
    }
    return child_idx;
}