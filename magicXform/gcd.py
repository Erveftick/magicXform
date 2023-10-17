from itertools import combinations
from math import gcd
import sys
from secrets import z3_path
sys.path.append(z3_path)
import z3

def find_gcd_and_combination(magic_values):
    """
    Calculate the greatest common divisor (GCD) of the entire list and 
    find a combination of elements that yields a GCD greater than or 
    equal to 2. If there is GCD < 2 - returns initial list and 1 as GCD
    """
    # Calculate the GCD of the entire list
    current_gcd = magic_values[0]
    for i in range(1, len(magic_values)):
        current_gcd = gcd(current_gcd, magic_values[i])
    
    # Check if the GCD is greater than 2 and return result instantly
    if current_gcd >= 2:
        return tuple(magic_values), current_gcd
    
    # If GCD is less than 2, try combinations by removing one element at a time
    n = len(magic_values)
    for i in range(n):
        combination = magic_values[:i] + magic_values[i+1:]
        current_gcd = combination[0]
        for j in range(1, len(combination)):
            current_gcd = gcd(current_gcd, combination[j])
            
        if current_gcd >= 2:
            return combination, current_gcd
    
    # If no suitable combination is found, return initial values and 1
    return magic_values, 1

def get_rules(magic_values, gcd):
    """
    Calculate coefficients for each element in 
    the list based on the given GCD.
    """
    coefficients = []
    for number in magic_values:
        coefficient = number // gcd
        if (coefficient > 1):
            coefficients.append((z3.IntVal(number) == z3.IntVal(coefficient) * z3.Int(f"GCD{gcd}")))
        else:
            coefficients.append((z3.IntVal(number) == z3.Int(f"GCD{gcd}")))
    return coefficients

def param_finder(magic_values):
    """
    Find parameters including GCD, coefficients, 
    and the remaining elements in the list.
    """
    combination, gcd = find_gcd_and_combination(magic_values)
    magic_set = set(magic_values)
    diff = list(magic_set.difference(combination))
    rules = get_rules(combination, gcd)
    return gcd, diff, magic_values, rules

def gcd_substituition(gcd):
    gcd_z3_var = z3.Int(f"GCD{gcd}")
    gcd_z3_int = z3.IntVal(gcd)
    gcd_range_rules = [(gcd_z3_var > 0), (gcd_z3_var <= gcd_z3_int)]
    # gcd_range_rules = [(gcd_z3_var == gcd_z3_int)]
    return gcd_range_rules, gcd_z3_var


# Example usage
# arr = [333,666,999]#[52, 97, 76, 80914] #[10, 15, 25, 30]
# result = find_gcd_and_combination(arr)
# print("param_finder:", param_finder(arr))
