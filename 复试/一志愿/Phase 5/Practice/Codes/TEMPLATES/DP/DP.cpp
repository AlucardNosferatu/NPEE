#include <map>
#include <string>
#include <set>

using namespace std;

class DP
{
public:
    map<string, string> dp;
    set<string> base_cases;
    map<string, string> (*depend_func)(string);
    string (*transit_func)(map<string, string>, string);
    bool (*base_check)(string, string &);

    DP(
        map<string, string> (*depend_func)(string),
        string (*transit_func)(map<string, string>, string),
        map<string, string> base_cases = {})
    {
        this->transit_func = transit_func;
        this->depend_func = depend_func;
        this->dp = map<string, string>{};
        this->base_cases = set<string>{};
        this->base_check = nullptr;
        if (!base_cases.empty())
        {
            for (const auto &pair : base_cases)
            {
                string state = pair.first;
                string dp_state = pair.second;
                this->set_base_case(state, dp_state);
            }
        }
    }

    void set_base_case(string state, string dp_state)
    {
        this->base_cases.insert(state);
        this->dp[state] = dp_state;
    }

    void set_base_check(bool (*base_check)(string, string &) = nullptr)
    {
        this->base_check = base_check;
    }

    string query(string state)
    {
        string res;
        bool base = false;
        if (this->base_check != nullptr)
        {
            base = this->base_check(state, res);
        }
        if (this->dp.count(state) > 0)
        {
            base = true;
            res = this->dp[state];
        }
        if (!base)
        {
            res = this->calculate(state);
        }
        return res;
    }

    string calculate(string state)
    {
        string res;
        map<string, string> depend_indices = this->depend_func(state);
        map<string, string> depend_dp_dict;
        for (const auto &pair : depend_indices)
        {
            string depend_title = pair.first;
            string depend_state = pair.second;
            string depend_dp = this->query(depend_state);
            depend_dp_dict[depend_title] = depend_dp;
        }
        res = this->transit_func(depend_dp_dict, state);
        this->dp[state] = res;
        return res;
    }
};