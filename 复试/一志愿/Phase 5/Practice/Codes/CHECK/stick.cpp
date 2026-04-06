#include <iostream>
#include <algorithm>
#include <cstring>
#include <functional>
#include <cassert>
using namespace std;

int n, sum, len;
int sticks[65];
bool used[65];

bool dfs(int cur, int need, int start, int depth)
{
    assert(depth <= 1000);

    // ===================== 分支1：递归成功终止 =====================
    if (cur == sum / len)
    {
        // 成立：所有木棍拼完 → 返回true
        return true;
    }
    /* else: cur < sum/len（没拼完所有木棍）→ 执行下面的逻辑 */

    // ===================== 分支2：当前木棍拼满 =====================
    if (need == 0)
    {
        // 成立：当前木棍凑满 → 递归拼下一根
        return dfs(cur + 1, len, start, depth + 1);
        // BUG1: 下一根备选木棍从0而不是start开始
        // 应修改为:
        // return dfs(cur + 1, len, 0, depth + 1);
    }
    /* else: need > 0（当前木棍还没拼满）→ 执行下面的循环逻辑 */

    // ===================== 分支3：遍历可选木棍 =====================
    if (need == len)
    {
        assert(start == 0);
    }
    for (int i = start; i < n; ++i)
    {
        // ===================== 子分支3.1：跳过已用木棍 =====================
        if (used[i])
        {
            // 成立：木棍已用 → 跳过当前i，继续下一个i
            continue;
        }
        /* else: 木棍未用 → 执行下面的逻辑 */

        // ===================== 子分支3.2：跳过过长木棍 =====================
        if (sticks[i] > need)
        {
            // 成立：木棍太长 → 跳过当前i，继续下一个i
            continue;
        }
        /* else: 木棍长度≤need（可用）→ 执行下面的逻辑 */

        // ===================== 子分支3.3：选中当前木棍并递归 =====================
        used[i] = true; // 标记已用
        if (dfs(cur, need - sticks[i], i + 1, depth + 1))
        {
            // 成立：递归成功 → 直接返回true（一路向上返回成功）
            return true;
        }
        /* else: 递归失败 → 执行下面的回溯+剪枝逻辑 */

        // ===================== 子分支3.4：回溯（取消标记） =====================
        used[i] = false; // 递归失败，取消标记

        // ===================== 子分支3.5：剪枝1（新木棍第一步失败） =====================
        if (need == len)
        {
            // 成立：拼新木棍的第一步就失败 → 直接返回false（这条路走不通）
            return false;
        }
        /* else: 不是新木棍第一步（已有部分拼接）→ 执行下面的剪枝2 */

        // ===================== 子分支3.6：剪枝2（跳过同长度木棍） =====================
        while (i + 1 < n && sticks[i + 1] == sticks[i])
        {
            // 成立：下一根木棍长度相同 → 跳过（i++）
            ++i;
        }
        /* else: 下一根长度不同/已到末尾 → 结束while，继续for循环的下一个i */
    }

    // ===================== 分支4：所有木棍遍历完都失败 =====================
    // 能走到这里，说明for循环里所有i都试了都不行 → 返回false
    return false;
}

bool is_prime(int x)
{
    if (x <= 1)
        return false;
    for (int i = 2; i * i <= x; ++i)
    {
        if (x % i == 0)
            return false;
    }
    return true;
}

int main()
{

    while (cin >> n && n)
    {
        sum = 0;
        for (int i = 0; i < n; ++i)
        {
            cin >> sticks[i];
            sum += sticks[i];
        }
        sort(sticks, sticks + n, greater<int>());
        int maxLen = sticks[0];
        // 对长度为len的棍子进行试探，看看能不能由长len的棍子构成全部
        bool flag = false;
        for (len = maxLen; len < sum; ++len)
        // BUG2: 遍历范围应该达到sum，闭区间
        // 当sum为素数时，唯一可能就是只有1根
        // 应修改为:
        // for (len = maxLen; len <= sum; ++len)
        {
            if (sum % len != 0)
                continue;
            memset(used, 0, sizeof(used));
            if (dfs(0, len, 0, 0))
            {
                flag = true;
                break;
            }
        }
        if (!flag)
        {
            len = -1;
        }
        if (is_prime(sum))
        {
            assert(len == sum);
        }
        cout << len << endl;
    }
    return 0;
}