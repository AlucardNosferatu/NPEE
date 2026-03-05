#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
using namespace std;

int main()
{
    int n, temp;
    vector<int> seq;
    scanf_s("%d", &n);
    for (int i = 0; i < n; i++)
    {
        scanf_s("%d", &temp);
        seq.push_back(temp);
    }
    stable_partition(
        seq.begin(), seq.end(),
        [](int x)
        {
            return x % 2 == 0;
        });
    string output = "";
    for (int i = 0; i < n; i++)
    {
        output = output + to_string(seq[i]) + " ";
    }
    output.pop_back();
    cout << output;
    return 0;
}