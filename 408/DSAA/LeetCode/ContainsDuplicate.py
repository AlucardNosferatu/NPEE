n = [1, 2, 3, 1]


def contains_duplicate(nums):
    nums.sort()
    for i in range(len(nums)):
        if i + 1 < len(nums) and nums[i] == nums[i + 1]:
            return True
    return False


print(contains_duplicate(n))
