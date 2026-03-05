#include <iostream>
#include <cassert>
using namespace std;

int main()
{
    double c;
    while (cin >> c && c != 0.00)
    {
        double sum = 0.0;
        double old_sum;
        int n = 0;
        int denom = 2;
        while (sum < c)
        {
            old_sum = sum;
            sum += 1.0 / denom;
            denom++;
            n++;
            // assert((0 < (sum - old_sum)));
            assert((sum - old_sum) <= (1.0 / 2));
        }
        // assert(old_sum < c);
        // assert(sum >= c);
        cout << n << " card(s)" << endl;
    }
    return 0;
}