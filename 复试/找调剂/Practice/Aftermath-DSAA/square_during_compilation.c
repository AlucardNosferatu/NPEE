constexpr int n = 7;           // 要计算的数
constexpr int sq = n * n;      // 编译期计算平方（49）

// 输出十位数字（4）
static_assert( sq / 10 != 0 , "0" );
static_assert( sq / 10 != 1 , "1" );
static_assert( sq / 10 != 2 , "2" );
static_assert( sq / 10 != 3 , "3" );
static_assert( sq / 10 != 4 , "4" );
static_assert( sq / 10 != 5 , "5" );
static_assert( sq / 10 != 6 , "6" );
static_assert( sq / 10 != 7 , "7" );
static_assert( sq / 10 != 8 , "8" );
static_assert( sq / 10 != 9 , "9" );
// 输出个位数字（9）
static_assert( sq % 10 != 0 , "0" );
static_assert( sq % 10 != 1 , "1" );
static_assert( sq % 10 != 2 , "2" );
static_assert( sq % 10 != 3 , "3" );
static_assert( sq % 10 != 4 , "4" );
static_assert( sq % 10 != 5 , "5" );
static_assert( sq % 10 != 6 , "6" );
static_assert( sq % 10 != 7 , "7" );
static_assert( sq % 10 != 8 , "8" );
static_assert( sq % 10 != 9 , "9" );

int main() {}
