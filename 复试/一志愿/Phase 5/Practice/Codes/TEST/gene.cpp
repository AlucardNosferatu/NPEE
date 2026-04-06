#define CUSTOM_CASE
#define CASE 2
#include <cassert>
#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
using namespace std;

int countInversions(const string &s)
{
    int cnt = 0;
    int n = s.length();
    if (n == 1)
        return 1;

    for (int i = 0; i < n; ++i)
    {
        for (int j = i + 1; j < n - 1; ++j)
        {
            if (s[i] > s[j])
                cnt++;
        }
    }
    return cnt;
}

int main()
{
    int n, m;
#ifdef CUSTOM_CASE
#if CASE == 1
    n = 1;
    m = 6;
    vector<string> case_input = {
        "A",
        "T",
        "T",
        "G",
        "C",
        "A"};
    vector<string> case_output = {
        "A",
        "T",
        "T",
        "G",
        "C",
        "A"};
#elif CASE == 2
    n = 3;
    m = 3;
    vector<string> case_input = {
        "AGC",
        "ACG",
        "CGA"};
    vector<string> case_output = {
        "ACG",
        "AGC",
        "CGA"};
#else
    n = 10;
    m = 6;
    vector<string> case_input = {
        "AACATGAAGG",
        "TTTTGGCCAA",
        "TTTGGCCAAA",
        "GATCAGATTT",
        "CCCGGGGGGA",
        "ATCGATGCAT"};
    vector<string> case_output = {
        "CCCGGGGGGA",
        "AACATGAAGG",
        "GATCAGATTT",
        "ATCGATGCAT",
        "TTTTGGCCAA",
        "TTTGGCCAAA"};
#endif
#else
    cin >> n >> m;
#endif
    vector<pair<int, string>> data;
    for (int i = 0; i < m; ++i)
    {
        string s;

#ifdef CUSTOM_CASE
        s = case_input[i];
#else
        cin >> s;
#endif
        int inv = countInversions(s);
        data.push_back({inv, s});
    }
    stable_sort(
        data.begin(), data.end(),
        [](const pair<int, string> &a, const pair<int, string> &b)
        {
            return a.first < b.first;
        });
    int i = 0;
    for (const auto &p : data)
    {
#ifdef CUSTOM_CASE
        assert(p.second == case_output[i]);
        i++;
#endif
        cout << p.second << endl;
    }
#ifdef CUSTOM_CASE
    assert(i == case_output.size());
#endif
    return 0;
}