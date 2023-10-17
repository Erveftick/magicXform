import os

def generate_command(folder_path):
    commands = []
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            command = f"python3 magicXform.py --pf=\"/home/ekvashyn/Code/magicXform/passed-challenges/{filename}\" --rf=\"{filename}\" --max_depth=300"
            commands.append(command)
    return commands

# Example folder path
folder_path = "/home/ekvashyn/Code/magicXform/passed-challenges"

# Generate commands for all files in the folder
commands = generate_command(folder_path)

# Print the generated commands
for command in commands:
    print(command)