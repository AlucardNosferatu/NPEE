#include <iostream>

int main03()
{
    //(a+100)=x^2
    //(a+268)=y^2
    //(a+268)-(a+100)=(y^2)-(x^2)
    //168=(y+x)(y-x)
    //y-x=2
    //y+x=84
    //2y=86
    //y=43
    int ypx;
    int y;
    int res;
    for (int i = 2; i < sqrt(168) + 1; i=i+2) {
        if (168 % i == 0) {
            ypx = 168 / i;
            y = (ypx + i) / 2;
            res = (y * y) - 268;
            if (res > 0)printf("%d\n", res);
        }
    }
    return 0;
}

//#include "math.h"
//#include "stdio.h"
//#include "conio.h"
//int main()
//{
//    long int i, x, y, z;
//    for (i = 1; i < 100000; i++)
//    {
//        x = sqrt(i + 100); /*x为加上100后开方后的结果*/
//        y = sqrt(i + 268); /*y为再加上168后开方后的结果*/
//        if (x * x == i + 100 && y * y == i + 268) /*如果一个数的平方根的平方等于该数，这说明此数是完全平方数*/
//            printf("\n%ld\n", i);
//    }
//    _getch();
//}
