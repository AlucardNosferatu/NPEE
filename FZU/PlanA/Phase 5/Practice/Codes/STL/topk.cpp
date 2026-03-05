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
    partial_sort(seq.begin(), seq.begin() + k, seq.end(), greater<int>());
    string output = "";
    for (int i = 0; i < k; i++)
    {
        output = output + to_string(seq[i]) + " ";
    }
    output.pop_back();
    cout << output;
    return 0;
}