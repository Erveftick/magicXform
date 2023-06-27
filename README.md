# magicXform
## A Magic Number Eliminator for CHC
This project provides a tool that accepts CHC as input and outputs a new version of the code with all "magic numbers" removed.

<img src="logo.png" width="20%" alt="Blaster Development" id="logo">

MagicXform is a Python-based tool for automatically refactoring CHC by eliminating magic numbers. It takes in CHC as input, identifies all instances of magic numbers, and replaces them with named constants to make the code more maintainable, understandable, and robust.

### Features
- Efficient parsing of CHC
- Identification of magic numbers
- Replacement of magic numbers with appropriately named constants
- The output of refactored CHC

### Dependencies

This project has the following dependencies:

- [Z3 Theorem Prover](https://github.com/Z3Prover/z3)

Please make sure you install dependencies mentioned above as appropriate. Provide a path to the modules in **secrets.py** as it was made in *secrets.sample.py*

This project also provides **requirements.txt** file with necessary PyPl dependencies.


### Installation
Clone the repository and navigate into the project directory:

```bash
git clone https://github.com/Erveftick/magicXform
cd magicXform

pip install -r requirements.txt
```

No additional installation steps are required as the script utilizes Python's built-in modules along with the Z3 Theorem Prover.

### Usage
Use the following command to run the script with the default input and output files:

```bash
python3 magicXform.py
```

By default, if no files are specified, the script will look for problem.smt2 as the input file and will write the output to result.smt2.

You can also specify custom problem and result files using the --pf and --rf parameters respectively:

```bash
python3 magicXform.py --pf my_problem.smt2 --rf my_result.smt2
```

### Structure
The main functionality of MagicXform includes:

- Parsing the input CHC and setting up the Fixedpoint object
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
