#include <string>
#include <unordered_map>
using namespace std;

int first_unique_char(string s)
{
    unordered_map<char, int> freq_map;
    for (int i = 0; i < s.length(); i++)
    {
        if (freq_map.count(s[i]) > 0)
        {
            freq_map[s[i]] = freq_map[s[i]] + 1;
        }
        else
        {
            freq_map[s[i]] = 1;
        }
    }
    for (int i = 0; i < s.length(); i++)
    {
        if (freq_map[s[i]] == 1)
        {
            return i;
        }
    }
    return -1;
}