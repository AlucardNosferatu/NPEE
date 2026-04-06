#include <iostream>
#include <cstring>
#include <algorithm>
#include <vector>
#include <cassert>
#include <set>
using namespace std;

int prosecution[205], defence[205], totalScore[205], diffScore[205];
int dp[25][805];
int lastSelected[25][805];

// 🐛 BUG 1：check 函数返回值取反，导致已选的人被误认为未选，或反之
bool check_selected(int count, int diffOffset, int candidate)
{
    // 遍历已选择的候选人名单，如果能遍历到底，说明这个人不在里面
    // 在里面的情况下，返回true才对
    while (count > 0 && candidate != lastSelected[count][diffOffset])
    {
        diffOffset -= diffScore[lastSelected[count][diffOffset]];
        count--;
    }
    // return count == 0; // 原应为 return a > 0; 现在 a==0 时返回 true（表示没找到），逻辑颠倒
    return count > 0; // 原应为 return a > 0; 现在 a==0 时返回 true（表示没找到），逻辑颠倒
}

int main()
{
    int n, m;
    int caseNum = 0;
    while (cin >> n >> m && n && m)
    {
        caseNum++;
        for (int i = 1; i <= n; ++i)
        {
            cin >> prosecution[i] >> defence[i];
            totalScore[i] = prosecution[i] + defence[i];
            diffScore[i] = prosecution[i] - defence[i];
        }

        int offset = 20 * m;
        int total = 2 * offset;

        memset(dp, -1, sizeof(dp));
        memset(lastSelected, 0, sizeof(lastSelected));
        dp[0][offset] = 0;
        // dp[i][j] = 用i个人，差值偏移后是j时，能达到的最大总和 S

        set<int> set_selected;
        for (int selected_i = 1; selected_i <= m; ++selected_i)
        {
            for (int diff_j = 0; diff_j <= total; ++diff_j)
            {
                if (dp[selected_i - 1][diff_j] == -1)
                {
                    continue;
                }
                else
                {
                    for (int candidate_k = 1; candidate_k <= n; ++candidate_k)
                    {
                        // 如果这个人被选中了就跳过
                        if (check_selected(selected_i - 1, diff_j, candidate_k))
                        {
                            assert(set_selected.count(candidate_k) > 0);
                            continue; // 因 BUG 1，此处判断可能相反
                        }
                        else
                        {
                            int newj = diff_j + diffScore[candidate_k];
                            if (newj < 0 || newj > total)
                            {
                                continue;
                            }
                            else
                            {
                                int newSum = dp[selected_i - 1][diff_j] + totalScore[candidate_k];
                                if (dp[selected_i][newj] < newSum)
                                {
                                    dp[selected_i][newj] = newSum;
                                    lastSelected[selected_i][newj] = candidate_k;
                                    set_selected.insert(candidate_k);
                                }
                            }
                        }
                    }
                }
            }
        }

        // 🐛 BUG 2：寻找最小差值时，只考虑负方向，忽略正方向的大小比较
        int ansJ;
        for (int j = 0; j <= offset; ++j)
        {
            bool check2 = false;
            // if (dp[m][offset - j] != -1)
            // 应当是二者都成立时选一个大的，而不是一个不成立才找另一个
            if ((dp[m][offset - j] != -1) || (dp[m][offset + j] != -1))
            {
                if (dp[m][offset - j] > dp[m][offset + j])
                {
                    ansJ = offset - j;
                    check2 = true;
                    break;
                }
                else
                {
                    ansJ = offset + j;
                    break;
                }
            }
            if (check2)
            {
                assert(dp[m][offset - j] > dp[m][offset + j]);
            }
        }

        vector<int> chosen;
        int curI = m, curJ = ansJ;
        while (curI > 0)
        {
            int k = lastSelected[curI][curJ];
            chosen.push_back(k);
            curJ -= diffScore[k];
            curI--;
        }
        sort(chosen.begin(), chosen.end());

        int totalSum = dp[m][ansJ];
        int diff = ansJ - offset;
        int pro = (totalSum + diff) / 2;
        int def = (totalSum - diff) / 2;

        cout << "Jury #" << caseNum << endl;
        cout << "Best jury has value " << pro << " for prosecution and value "
             << def << " for defence:" << endl;
        for (int i = 0; i < chosen.size(); ++i)
        {
            cout << " " << chosen[i];
        }
        cout << endl
             << endl;
    }
    return 0;
}