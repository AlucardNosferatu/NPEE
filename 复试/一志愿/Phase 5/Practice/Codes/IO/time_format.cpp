#include <iostream>

using namespace std;
int main()
{
    int h, m, s;
    bool pm;
    while (1)
    {
        scanf_s("%d %d %d", &h, &m, &s);
        pm = false;
        if (h > 12)
        {
            pm = true;
            h = h - 12;
        }
        else if (h == 12)
        {
            if (m > 0 || s > 0)
            {
                pm = true;
            }
        }
        else if (h == 0)
            h = 12;
        if (pm)
            printf("%02d:%02d:%02d PM\n", h, m, s);
        else
            printf("%02d:%02d:%02d AM\n", h, m, s);
    }
}