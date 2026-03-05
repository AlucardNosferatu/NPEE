#include <iostream>
#include <vector>
#include <cassert>
using namespace std;

int main12() {
	for (int num = 101; num <= 200; num = num + 2) {
		assert(num % 2 != 0);
		bool ok = true;
		for (int factor = 3; factor <= ceil(sqrt(num)); factor = factor + 2) {
			if (num % factor == 0) {
				ok = false;
				break;
			}
		}
		if(ok)
			printf("%d ",num);
	}
	return 0;
}