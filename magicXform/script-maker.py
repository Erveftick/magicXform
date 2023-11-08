import os, csv

# Example folder path
folder_path = "/home/ekvashyn/Code/mXf/magicXform/challenges"

# def generate_command(folder_path):
#     commands = []
#     for filename in os.listdir(folder_path):
#         if os.path.isfile(os.path.join(folder_path, filename)):
#             command = f"python3 magicXform.py --pf=\"{folder_path}/{filename}\" --rf=\"{filename}\" --max_depth=300 --ver=1"
#             commands.append(command)
#     return commands

def generate_command(folder_path):
    commands = []
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            command = f"python3 magicXform.py --pf=\"{folder_path}/{filename}\" --rf=\"{filename}\" --max_depth=300 --ver=2"
            commands.append(command)
    return commands

# Generate commands for all files in the folder
commands = generate_command(folder_path)

csv_file = "run_script.csv"

# Print the generated commands
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file, quoting=csv.QUOTE_NONE, quotechar='',escapechar='')
    
    # Write the data to the CSV file
    for command in commands:
        writer.writerow([command])

# for command in commands:
#     print(command)

print(f"Data has been written to {csv_file}")