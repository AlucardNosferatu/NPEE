nums = [4, 1, 2, 1, 2]

for i in range(1, len(nums)):
    nums[0] ^= nums[i]

print("Done")
