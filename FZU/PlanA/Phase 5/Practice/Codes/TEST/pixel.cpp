#define CASE 1
#include <cassert>
#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <string>
using namespace std;

typedef long long ll;

struct Point
{
    ll pos;  // 1-based 位置
    int val; // 边缘值
    Point(ll p, int v) : pos(p), val(v) {}
};

// 根据绝对位置（1-based）获取原始像素值
int getValue(const vector<pair<int, ll>> &rle, ll pos)
{
    ll cnt = 0;
    for (size_t i = 0; i < rle.size(); ++i)
    {
        cnt += rle[i].second;
        if (cnt >= pos)
            return rle[i].first;
    }
    return 0; // never reach
}

// 计算指定位置（1-based）的边缘值
int computeEdge(const vector<pair<int, ll>> &rle, ll pos, int w, ll total)
{
    int val = getValue(rle, pos);
    int maxDiff = 0;
    ll r = (pos - 1) / w;
    ll c = (pos - 1) % w;
    ll h = total / w;
    for (int dr = -1; dr <= 1; ++dr)
    {
        for (int dc = -1; dc <= 1; ++dc)
        {
            if (dr == 0 && dc == 0)
                continue;
            // Bug2: 忽略对角线邻居（只考虑上下左右）
            if (dr != 0 && dc != 0)
                continue; // 只保留四邻域
            ll nr = r + dr;
            ll nc = c + dc;
            if (nr >= 0 && nr < h && nc >= 0 && nc < w)
            {
                ll npos = nr * w + nc + 1;
                int nval = getValue(rle, npos);
                int diff = abs(val - nval);
                if (diff > maxDiff)
                    maxDiff = diff;
            }
        }
    }
    return maxDiff;
}

string build_output(int val, ll pos)
{
    string output_string = to_string(val) + ' ' + to_string(pos) + '\n';
    return output_string;
}

int main()
{
#ifdef CASE
    int i = 0;
    int j = 0;
    int k = 0;
#endif
#if CASE == 1
    vector<int> vector_w = {
        7,
        10,
        3,
        0};
    vector<vector<int>> vector_v = {
        {15, 100, 25, 175, 25, 175, 25, 0},
        {35, 200, 0},
        {255, 10, 255, 10, 255, 10, 255, 0}};
    vector<vector<int>> vector_l = {
        {4, 15, 2, 2, 5, 2, 5, 0},
        {500000000, 500000000, 0},
        {1, 1, 2, 1, 2, 1, 1, 0}};
    vector<vector<string>> vector_a = {
        {"85 5\n", "0 2\n", "85 5\n", "75 10\n", "150 2\n", "75 3\n", "0 2\n", "150 2\n", "0 4\n"},
        {"0 499999990\n", "165 20\n", "0 499999990\n"},
        {"245 9\n"}};
#elif CASE == 2
    vector<int> vector_w = {
        2,
        0};
    vector<vector<int>> vector_v = {
        {255, 0}};
    vector<vector<int>> vector_l = {
        {2, 0}};
    vector<vector<string>> vector_a = {
        {"0 2\n"}};
#elif CASE == 3
    vector<int> vector_w = {
        3,
        0};
    vector<vector<int>> vector_v = {
        {0, 255, 0, 0}};
    vector<vector<int>> vector_l = {
        {1, 1, 1, 0}};
    vector<vector<string>> vector_a = {
        {"255 3\n"}};
#elif CASE == 4
    vector<int> vector_w = {
        2,
        0};
    vector<vector<int>> vector_v = {
        {10, 20, 0}};
    vector<vector<int>> vector_l = {
        {2, 2, 0}};
    vector<vector<string>> vector_a = {
        {"10 4\n"}};
#elif CASE == 5
    vector<int> vector_w = {
        1000,
        0};
    vector<vector<int>> vector_v = {
        {100, 0}};
    vector<vector<int>> vector_l = {
        {1000000000, 0}};
    vector<vector<string>> vector_a = {
        {"0 1000000000\n"}};
#endif

    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int w;

#ifdef CASE
    w = vector_w[i];
    int cin_ref = 1;
#else
    istream &cin_ref = cin >> w;
#endif

    while (cin_ref && w)
    {
        vector<pair<int, ll>> rle; // (value, length)
        int v;
        ll l;

#ifdef CASE
        v = vector_v[i][j];
        l = vector_l[i][j];
#else
        cin >> v >> l;
#endif

        while (cin_ref && (v || l))
        {
            rle.push_back({v, l});
#ifdef CASE
            j++;
            v = vector_v[i][j];
            l = vector_l[i][j];
#else
            cin >> v >> l;
#endif
        }

        // 计算总像素数和高度
        ll total = 0;
        for (auto &p : rle)
            total += p.second;
        ll h = total / w;

        vector<Point> points;

        // 处理每个RLE块的起始点
        ll curPos = 1; // 当前块的起始位置（1-based）
        for (size_t i = 0; i < rle.size(); ++i)
        {
            ll r = (curPos - 1) / w;
            ll c = (curPos - 1) % w;
            // 遍历起始点的四邻域（Bug1：只考虑四邻域，忽略对角线）
            for (int dr = -1; dr <= 1; ++dr)
            {
                for (int dc = -1; dc <= 1; ++dc)
                {
                    // Bug1: 只保留四邻域
                    if (dr == 0 && dc == 0)
                        continue;
                    if (dr != 0 && dc != 0)
                        continue;
                    ll nr = r + dr;
                    ll nc = c + dc;
                    if (nr >= 0 && nr < h && nc >= 0 && nc < w)
                    {
                        ll npos = nr * w + nc + 1;
                        int edgeVal = computeEdge(rle, npos, w, total);
                        points.push_back(Point(npos, edgeVal));
                    }
                }
            }
            curPos += rle[i].second;
        }

        // 处理虚拟点（图像结束后的第一个位置）的八邻域
        ll vr = h; // 虚拟点的行（0-based）
        ll vc = 0;
        for (int dr = -1; dr <= 1; ++dr)
        {
            for (int dc = -1; dc <= 1; ++dc)
            {
                ll nr = vr + dr;
                ll nc = vc + dc;
                if (nr >= 0 && nr < h && nc >= 0 && nc < w)
                {
                    ll npos = nr * w + nc + 1;
                    int edgeVal = computeEdge(rle, npos, w, total);
                    points.push_back(Point(npos, edgeVal));
                }
            }
        }

        // 按位置排序
        sort(points.begin(), points.end(),
             [](const Point &a, const Point &b)
             { return a.pos < b.pos; });

        string output;
        // 输出当前图像
        cout << w << '\n';
        if (!points.empty())
        {
            size_t cur = 0;
#ifdef CASE
            k = 0;
#endif
            for (size_t i_ = 0; i_ < points.size(); ++i_)
            {
                if (points[cur].val == points[i_].val)
                    continue;
                output = build_output(points[cur].val, points[i_].pos - points[cur].pos);
#ifdef CASE
                assert(vector_a[i][k] == output);
                k++;
#endif
                cout << output;
                cur = i_;
            }
            output = build_output(points[cur].val, total - points[cur].pos + 1);
#ifdef CASE
            assert(vector_a[i][k] == output);
            k++;
#endif
            cout << output;
        }
        else
        {
            output = build_output(0, total);
            // 理论上不会发生，但以防万一
            cout << output;
        }
        output = build_output(0, 0);
        cout << output;
#ifdef CASE
        i++;
        j = 0;
        w = vector_w[i];
#else
        cin >> w;
#endif
    }
    cout << "0\n";
    return 0;
}