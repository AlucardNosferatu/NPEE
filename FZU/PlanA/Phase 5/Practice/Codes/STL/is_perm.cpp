#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main()
{
    int temp;
    int count1;
    vector<int> list1;
    int count2;
    vector<int> list2;

    scanf("%d", &count1);
    for (int i = 0; i < count1; i++)
    {
        if (i == count1 - 1)
        {
            scanf("%d", &temp);
        }
        else
        {
            scanf("%d ", &temp);
        }
        list1.push_back(temp);
    }
    bool is_p;
    scanf("%d", &count2);
    if (count1 == count2)
    {
        for (int i = 0; i < count2; i++)
        {
            if (i == count2 - 1)
            {
                scanf("%d", &temp);
            }
            else
            {
                scanf("%d ", &temp);
            }
            list2.push_back(temp);
        }
        is_p = is_permutation(list1.begin(), list1.end(), list2.begin());
    }
    else
    {
        is_p = false;
    }
    printf("%s\n", is_p ? "true" : "false");
    return 0;
}