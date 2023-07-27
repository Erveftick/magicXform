GSpacer_solved_challenges = [1, 2, 4, 5, 6, 7, 18, 19, 23, 26, 29, 34, 35, 36, 37, 38, 39, 42, 46]
mypath = "/home/ekvashyn/Code/magicXform/results"

from os import walk

def get_files(path):
    return next(walk(path), (None, None, []))[2]

def get_numbers(a):
    return sorted([int(i.split('_')[-1].split('.')[0]) for i in a])

def compare_lists(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    
    difference_1 = sorted(set1.difference(set2))
    difference_2 = sorted(set2.difference(set1))
    
    return difference_1, difference_2


sat_filenames = get_files(mypath + "/SAT")
sat_challenge_numbers = get_numbers(sat_filenames)
diff_1, diff_2 = compare_lists(sat_challenge_numbers, GSpacer_solved_challenges)

def print_table(sat, magic, spacer):
    print("| Challenge type | Amount | Challenges |")
    print("|---|---|---|")
    print(f"| SAT resolved | {len(sat)} | {', '.join(map(str, sat))} |")
    print(f"| Diff: magicXform | {len(magic)}| {', '.join(map(str, magic))} |")
    print(f"| Diff: GSpacer | {len(spacer)}| {', '.join(map(str, spacer))} |")

print_table(sat_challenge_numbers, diff_1, diff_2)
