#include <iostream>
#include <vector>
using namespace std;

int main11() {
    int months = 10;
    int big_rabbits = 1;      // 初始大兔子
    int small_rabbits = 0;    // 真正的小兔子总数
    vector<pair<int, int>> mature_queue;  // <数量, 倒计时>
    for (int i = 0; i < months; i++) {
        int current_month = i + 1;
        cout << "===== 第" << current_month << "个月 =====\n";

        // 1. 所有待成熟兔子倒计时-1
        for (auto& p : mature_queue) {
            p.second--;
        }

        // 2. 成熟的兔子：从队列删掉，从小兔子里减掉，加到大兔子
        int mature_this_month = 0;

        for (auto it = mature_queue.begin(); it != mature_queue.end();) {
            if (it->second <= 0) {
                mature_this_month += it->first;
                it = mature_queue.erase(it);  // 删掉这一批
            }
            else {
                ++it;
            }
        }

        // ✅ 这里才是关键修复！
        small_rabbits -= mature_this_month;  // 小兔子变少
        big_rabbits += mature_this_month;    // 大兔子变多

        // 3. 大兔子生新兔子
        int new_born;
        if (current_month >= 3) {
            new_born = big_rabbits;
        }
        else {
            new_born = 0;
        }
        small_rabbits += new_born;            // 小兔子增加
        if (new_born > 0) {
            mature_queue.push_back({ new_born, 2 });// 加入成熟队列，3个月成熟
        }

        // 输出看是否正确
        //cout << "大兔子：" << big_rabbits << endl;
        //cout << "小兔子：" << small_rabbits << endl;
        cout << "总兔子：" << big_rabbits + small_rabbits << endl;
        cout << endl;
    }
    return 0;
}