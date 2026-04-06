#include <iostream>


int main02()
{
	long int i;
	int over_100w, over_60w, over_40w, over_20w, over_10w, over_0w;
	while (1) {
		scanf_s("%ld", &i);
		over_100w = i - 1000000;
		if (over_100w < 0)over_100w = 0;
		over_60w = i - 600000 - over_100w;
		if (over_60w < 0)over_60w = 0;
		over_40w = i - 400000 - over_100w - over_60w;
		if (over_40w < 0)over_40w = 0;
		over_20w = i - 200000 - over_100w - over_60w - over_40w;
		if (over_20w < 0)over_20w = 0;
		over_10w = i - 100000 - over_100w - over_60w - over_40w - over_20w;
		if (over_10w < 0)over_10w = 0;
		over_0w = i - over_100w - over_60w - over_40w - over_20w - over_10w;
		if (over_0w < 0)over_0w = 0;
		over_0w = over_0w * 0.1;
		over_10w = over_10w * 0.075;
		over_20w = over_20w * 0.05;
		over_40w = over_40w * 0.03;
		over_60w = over_60w * 0.015;
		over_100w = over_100w * 0.01;
		printf("bonus=%d\n", over_0w + over_10w + over_20w + over_40w + over_60w + over_100w);
	}
	return 0;
}