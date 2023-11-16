import os

def calculate_average(filename):
    parts = filename.split('-')
    if len(parts) < 2:
        return None

    try:
        num = float(parts[0])
        return num
    except ValueError:
        return None

def group_filenames_by_second_part(folder_path):
    grouped_files = {}
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            parts = filename.split('-', 1)
            if len(parts) < 2:
                continue

            second_part = parts[1].strip()
            num = calculate_average(filename)

            if second_part in grouped_files:
                grouped_files[second_part].append(num)
            else:
                grouped_files[second_part] = [num]

    return grouped_files

def calculate_average_for_groups(grouped_files):
    averages = {}
    for second_part, nums in grouped_files.items():
        valid_nums = [num for num in nums if num is not None]
        if valid_nums:
            average = sum(valid_nums) / len(valid_nums)
            formatted_average = "{:.2f}".format(average)
            averages[second_part] = formatted_average

    return averages

# Example folder path
folder_path = "/Users/ekvashyn/Code/mXf/magicXform/magicXform/tmp"

# Group filenames by second part and calculate averages
grouped_files = group_filenames_by_second_part(folder_path)
averages = calculate_average_for_groups(grouped_files)

# Print the calculated averages for each group
sorted_averages = sorted(averages.items(), key=lambda x: x[0])  # Sort by problem name
print("|     Problem     |   Time   |")
print("|-----------------|----------|")
for second_part, average in sorted_averages:
    print(f"| {second_part} | {average}s |")
print("")
print(f"Total: {len(averages.items())}")

# nums = []
# for second_part, average in sorted_averages:
#     _, _, num = second_part.split("_", 2)
#     num, _ = num.split(".", 1)
#     nums.append(num)
# # print(nums)
# number_list = set([str(i).zfill(2) for i in range(1, 59)])
# print(list(number_list.difference(set(nums))))

# for i in list(number_list.difference(set(nums))):
#     print("python3 magicXform.py --pf=\"/home/ekvashyn/Code/mXf/magicXform/challenges/s_split_52.smt2\" --rf=\"s_split_52.smt2\" --max_depth=300 --ver=2"
# )