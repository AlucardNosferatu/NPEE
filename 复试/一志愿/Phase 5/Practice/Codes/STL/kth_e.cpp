#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main()
{
    int temp;
    int e_count;
    int k;
    int res;
    vector<int> int_list;

    scanf("%d", &e_count);
    for (int i = 0; i < e_count; i++)
    {
        if (i == e_count - 1)
        {
            scanf("%d", &temp);
        }
        else
        {
            scanf("%d ", &temp);
        }
        int_list.push_back(temp);
    }
    scanf("%d", &k);

    nth_element(int_list.begin(), int_list.begin() + k - 1, int_list.end());
    printf("%d\n", int_list[k - 1]);
    return 0;
}