#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
using namespace std;

int main()
{
    int n, k, temp;
    vector<int> seq;
    scanf_s("%d %d", &n, &k);
    for (int i = 0; i < n; i++)
    {
        scanf_s("%d", &temp);
        seq.push_back(temp);
    }

    inplace_merge(seq.begin(), seq.begin() + k, seq.end());

    string output = "";
    for (int i = 0; i < n; i++)
    {
        output = output + to_string(seq[i]) + " ";
    }
    output.pop_back();
    cout << output;
    return 0;
}