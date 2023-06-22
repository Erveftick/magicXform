# magicXform
## A Magic Number Eliminator for Datalog Code
This project provides a tool that accepts Datalog code as input and outputs a new version of the code with all "magic numbers" removed.

Logo

MagicXform is a Python-based tool for automatically refactoring Datalog code by eliminating magic numbers. It takes in Datalog code as input, identifies all instances of magic numbers, and replaces them with named constants to make the code more maintainable, understandable, and robust.

### Features
- Efficient parsing of Datalog code
- Identification of magic numbers
- Replacement of magic numbers with appropriately named constants
- The output of refactored Datalog code

### Prerequisites
- Python 3
- Z3 Theorem Prover (version 4.12.2 or older)

### Installation
Clone the repository and navigate into the project directory:

```bash
git clone https://github.com/Erveftick/magicXform
cd magicXform

pip z3
pip argparse
```

No additional installation steps are required as the script utilizes Python's built-in modules along with the Z3 Theorem Prover.

### Usage
Use the following command to run the script with the default input and output files:

```bash
python3 magicXform.py

# You can also specify custom problem and result files using the --pf and --rf parameters respectively:
python3 magicXform.py --pf my_problem.smt2 --rf my_result.smt2
```
By default, if no files are specified, the script will look for problem.smt2 as the input file and will write the output to result.smt2.

### Structure
The main functionality of MagicXform includes:

- Parsing the input Datalog code and setting up the Fixedpoint object
- Identifying magic numbers and preparing replacements
- Replacing the magic numbers and generating new rules
- Handling invariants and generating additional conditions
- Setting up a new Fixedpoint with the new rules and variables
- Writing the result to console and to the output file
- Optionally processing Horn clauses if present

### Contributing
Contributions, issues, and feature requests are welcome. Please feel free to check issues page if you want to contribute.

### License
Distributed under the MIT License. See LICENSE for more information.

Enjoy using MagicXform!
