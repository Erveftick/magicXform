import math
from functools import reduce
def find_gcd(list):
    x = reduce(math.gcd, list)
    return x

def get_coefficients(numbers_list, delimiter):
    coefficients = []
    for number in numbers_list:
        coefficient = number // delimiter
        coefficients.append(f"(* {coefficient} {delimiter})")
    return coefficients

def relation_finder(magic_values, substitutions):
    print(f"magic_values: {magic_values}" )
    magicGCD = find_gcd(magic_values)
    return get_coefficients(magic_values, magicGCD)

# numbers_list = [7500, 12500, 2500, 15000]
numbers_list = [4000,5000,6000,10000]
# numbers_list = [3333,6666,9999]
# numbers_list = [52, 97, 76, 80914]
delimiter = find_gcd(numbers_list)

coefficients = relation_finder(numbers_list, 1)
print(coefficients)  # Output: [4, 5, 6, 10]

# print("The greatest non-divisible number is:", result)
