nums1 = [4,9,5]
nums2 = [9,4,9,8,4]

ret = []
# for i in range(len(nums1)):
#     if nums1[i] in nums2:
#         ret.append(nums1[i])
#         nums2.remove(nums1[i])

nums1.sort()
nums2.sort()
i, j = 0, 0
while i < len(nums1) and j < len(nums2):
    if nums1[i] == nums2[j]:
        ret.append(nums1[i])
        i += 1
        j += 1
    elif nums1[i] < nums2[j]:
        i += 1
    else:
        j += 1

print('Done')
