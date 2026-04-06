#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main()
{
    int temp;
    int count1;
    vector<int> list1;

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
    next_permutation(list1.begin(), list1.end());
    for (int i = 0; i < count1; i++)
    {
        printf("%d", list1[i]);
        printf("%s", i == list1.size() - 1 ? "\n" : " ");
    }
    return 0;
}