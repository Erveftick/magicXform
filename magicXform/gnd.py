from fractions import gcd
from functools import reduce
def find_gcd(list):
    x = reduce(gcd, list)
    return x

# numbers_list = [7500, 12500, 2500, 15000]
# numbers_list = [4000,5000,6000,10000]
# numbers_list = [3333,6666,9999]
numbers_list = [1000, 2000, 3000]
result = find_gcd(numbers_list)
print("The greatest non-divisible number is:", result)
