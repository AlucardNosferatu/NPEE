#include <iostream>
#include <algorithm>
#include <vector>
using namespace std;
int main()
{
    int temp;
    int set_count;
    vector<int> set1;
    vector<int> set2;

    scanf("%d", &set_count);
    for (int i = 0; i < set_count; i++)
    {
        if (i == set_count - 1)
        {
            scanf("%d", &temp);
        }
        else
        {
            scanf("%d ", &temp);
        }
        set1.push_back(temp);
    }
    scanf("%d", &set_count);
    for (int i = 0; i < set_count; i++)
    {
        if (i == set_count - 1)
        {
            scanf("%d", &temp);
        }
        else
        {
            scanf("%d ", &temp);
        }
        set2.push_back(temp);
    }
    // 2. 定义容器存交集结果（用vector/set都可以）
    vector<int> result;

    // 3. 求交集：用back_inserter自动扩容
    set_intersection(
        set1.begin(), set1.end(),
        set2.begin(), set2.end(),
        back_inserter(result) // 自动往result里加元素，不用提前分配空间
    );
    for (int i = 0; i < result.size(); i++)
    {
        if (i == result.size() - 1)
        {
            printf("%d", result[i]);
        }
        else
        {
            printf("%d ", result[i]);
        }
    }
    printf("\n");
    return 0;
}