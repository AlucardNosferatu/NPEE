#include <string>
#include <unordered_map>
using namespace std;
bool is_valid_parentheses(string s)
{
    unordered_map<char, char> paren_map = {{')', '('}, {']', '['}, {'}', '{'}};
    vector<char> stack;
    for (const char &ch : s)
    {
        if (paren_map.count(ch) <= 0)
        {
            stack.push_back(ch);
        }
        else
        {
            if (stack.empty() || stack.back() != paren_map.at(ch))
            {
                return false;
            }
            stack.pop_back();
        }
    }
    return stack.size() == 0;
}