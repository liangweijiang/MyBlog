from django.test import TestCase


# Create your tests here.
def maxProduct(nums) -> int:
    if not nums: return 0
    # 目前的累乘
    res = nums[0]
    res_min = nums[0]
    res_max = nums[0]
    for num in nums[1:]:
        cur_max = max(res_max * num, res_min * num, num)
        cur_min = min(res_max * num, res_min * num, num)
        print('cur_max', cur_max)
        print('cur_min', cur_min)
        res = max(res, cur_max)
        print('res', res)
        res_max = cur_max
        res_min = cur_min
        print('res_max', res_max)
        print('res_min', res_min)
    return res


print(maxProduct([6, 3, -10, 0, 2, -6, 8, -7, 4, 6]))
