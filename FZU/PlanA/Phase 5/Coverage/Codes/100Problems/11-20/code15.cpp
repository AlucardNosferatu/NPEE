#include <iostream>
#include <vector>
#include <cassert>
using namespace std;

int main15() {
    int score;
    char grade;
    printf("please input a score\n");
    scanf_s("%d", &score);
    grade = score >= 90 ? 'A' : (score >= 60 ? 'B' : 'C');
    printf("%d belongs to %c", score, grade);
    return 0;
}