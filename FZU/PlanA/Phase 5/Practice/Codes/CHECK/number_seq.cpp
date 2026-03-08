#include <cstdio>
#include <algorithm>
#include <cmath>
#include <cassert>

using namespace std;

// 2bit 編碼：偶數位 = 前置異常，奇數位 = 後置異常
const unsigned long long PRE_GETBIT = 1ULL << 0;  // getbit 前置
const unsigned long long POST_GETBIT = 1ULL << 1; // getbit 後置
const unsigned long long PRE_M1 = 1ULL << 2;      // M1 共用前置
const unsigned long long POST_CNT = 1ULL << 3;    // cnt 範圍後置
const unsigned long long POST_REMAIN = 1ULL << 5; // remain 範圍後置
const unsigned long long PRE_M2 = 1ULL << 6;      // M2 共用前置
const unsigned long long POST_NUM = 1ULL << 7;    // num 範圍後置
const unsigned long long POST_DIGIT = 1ULL << 9;  // digit 合法後置

// 目標模式：後置全異常，前置全正常 → bit1,3,5,7,9 = 1
const unsigned long long TARGET_010101 = POST_GETBIT | POST_CNT | POST_REMAIN | POST_NUM | POST_DIGIT;

unsigned long long error_mask = 0;

int getbit(int x)
{
    // 前置檢查：只記錄
    if (x <= 0)
    {
        error_mask |= PRE_GETBIT;
    }

    int cnt = 0;
    int temp = x;
    while (temp > 0)
    {
        temp /= 10;
        cnt++;
    }

    // 後置檢查：只記錄（例如返回值範圍）
    if (cnt < 1 || cnt > 10)
    { // 正常數字位數 1~10
        error_mask |= POST_GETBIT;
    }

    return cnt;
}

void module1_accumulate_position(int N_in, int &cnt_out, int &remain_out)
{
    // 前置組：只記錄
    if (N_in < 1)
    {
        error_mask |= PRE_M1;
    }

    int cur_total = 1;
    int cnt = 1;
    int N = N_in >= 1 ? N_in : 1; // 防護

    while (true)
    {
        if (N <= cur_total)
            break;
        N -= cur_total;
        cnt++;
        cur_total += getbit(cnt);
    }

    // 後置 C：cnt 範圍
    if (!(cnt >= 1 && cnt <= 2000000000))
    {
        error_mask |= POST_CNT;
    }

    // 後置 D：remain 範圍
    if (!(N >= 1 && N <= cur_total))
    {
        error_mask |= POST_REMAIN;
    }

    cnt_out = cnt;
    remain_out = N;
}

void module2_locate_digit(int remain_in, int cnt_in, int &digit_out)
{
    // 前置組：只記錄
    if (cnt_in < 1 || remain_in < 1)
    {
        error_mask |= PRE_M2;
    }

    int cur = 1;
    int num = 1;
    int remain = remain_in >= 1 ? remain_in : 1;

    while (true)
    {
        if (remain <= cur)
            break;
        remain -= cur;
        num++;
        cur = getbit(num);
    }

    // 後置 H：num 範圍
    if (!(num >= 1 && num <= 2000000000))
    {
        error_mask |= POST_NUM;
    }

    int digit;
    if (cur == remain)
    {
        digit = num % 10;
    }
    else
    {
        digit = (int)(num / pow(10, cur - remain)) % 10;
    }

    // 後置 J：digit 合法
    if (!(digit >= 0 && digit <= 9))
    {
        error_mask |= POST_DIGIT;
    }

    digit_out = digit;
}

void final_error_check()
{
    // 只檢查目標模式 010101（後置全異常，前置全正常）
    if ((error_mask & TARGET_010101) == TARGET_010101 &&
        (error_mask & ~TARGET_010101) == 0)
    {
        assert(false && "目標模式 010101 觸發（後置全異常，前置正常）");
    }

    // 暫時不觸發其它情況（為了測試 010101）
    // 如果要完整檢查，可以加回原來的从严到宽松斷言
}

int main()
{
    int T;
    scanf("%d", &T);

    while (T--)
    {
        int N;
        scanf("%d", &N);

        error_mask = 0;

        int cnt, remain;
        module1_accumulate_position(N, cnt, remain);

        int digit;
        module2_locate_digit(remain, cnt, digit);

        final_error_check();

        printf("%d\n", digit);
    }
    return 0;
}