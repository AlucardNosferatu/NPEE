#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
using namespace std;

int main()
{
    int n1, n2, temp;
    vector<int> seq1;
    vector<int> seq2;
    scanf_s("%d", &n1);
    for (int i = 0; i < n1; i++)
    {
        scanf_s("%d", &temp);
        seq1.push_back(temp);
    }
    scanf_s("%d", &n2);
    for (int i = 0; i < n2; i++)
    {
        scanf_s("%d", &temp);
        seq2.push_back(temp);
    }
    bool inc = includes(seq1.begin(), seq1.end(), seq2.begin(), seq2.end());

    string output = inc ? "true" : "false";
    cout << output;
    return 0;
}