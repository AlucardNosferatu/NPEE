#include <iostream>
#include <map>
#include <string>
#include <functional>
#include <string>
// 全局缓存
std::map<std::string, int> dp_cache;

// 核心函数类型定义
using GetDependencies = std::function<std::map<std::string, std::string>(const std::string &)>;
using Transition = std::function<int(const std::string &, const std::map<std::string, int> &)>;
// is_base 改为返回 bool 并通过引用传出值
using IsBase = std::function<bool(const std::string &, int &)>;

struct Funcs
{
    GetDependencies get_dependencies;
    Transition transition;
    IsBase is_base; // 返回 bool，值通过引用传出
};

int dp(const std::string &state, const Funcs &funcs)
{
    auto it = dp_cache.find(state);
    if (it != dp_cache.end())
        return it->second;

    // 检查基础情况
    if (funcs.is_base)
    {
        int base_val;
        if (funcs.is_base(state, base_val))
        {
            dp_cache[state] = base_val;
            return base_val;
        }
    }

    auto deps = funcs.get_dependencies(state);
    std::map<std::string, int> dep_values;
    for (const auto &pair : deps)
    {
        const std::string &key = pair.first;
        const std::string &dep_state = pair.second;
        dep_values[key] = dp(dep_state, funcs);
    }

    int result = funcs.transition(state, dep_values);
    dp_cache[state] = result;
    return result;
}

void clear_cache()
{
    dp_cache.clear();
}

std::map<std::string, std::string> fib_deps(const std::string &s)
{
    int n = std::stoi(s);
    std::map<std::string, std::string> deps;
    if (n >= 1)
        deps["prev1"] = std::to_string(n - 1);
    if (n >= 2)
        deps["prev2"] = std::to_string(n - 2);
    return deps;
}

int fib_trans(const std::string &s, const std::map<std::string, int> &deps)
{
    int val1 = deps.count("prev1") ? deps.at("prev1") : 0;
    int val2 = deps.count("prev2") ? deps.at("prev2") : 0;
    return val1 + val2;
}

bool fib_base(const std::string &s, int &val)
{
    int n = std::stoi(s);
    if (n == 0)
    {
        val = 0;
        return true;
    }
    if (n == 1)
    {
        val = 1;
        return true;
    }
    return false;
}

int fib(int n)
{
    clear_cache();
    Funcs funcs{fib_deps, fib_trans, fib_base};
    return dp(std::to_string(n), funcs);
}

int main()
{
    std::cout << fib(10) << std::endl; // 55
    return 0;
}