#include <vector>
#include <iostream>
using namespace std;
int find_pfc(vector<int> int_list, int target)
{
START:
    int i = 0; // 变量定义
    int current_int;
    int res;
    goto GET_CURRENT;
GET_CURRENT:
    current_int = int_list[i];
    goto COMPARE;
COMPARE:
    if (current_int == target)
    {
        res = i;
        goto RETURN_RES;
    }
    else
        goto INC_INDEX;

RETURN_RES:
    return res;
INC_INDEX:
    i++;
    if (i >= int_list.size())
    {
        res = -1;
        goto RETURN_RES;
    }
    else
        goto GET_CURRENT;
}

int main()
{
    vector<int> int_list_ = {0, 1, 2, 3, 4, 5, 6};
    int res;
    res = find_pfc(int_list_, 4);
    cout << res << endl;
    res = find_pfc(int_list_, 7);
    cout << res << endl;
    return 0;
}