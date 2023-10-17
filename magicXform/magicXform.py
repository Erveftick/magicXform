import sys
import os
from secrets import z3_path, z3_eval_path
from spinner import Loader
from gcd import *
sys.path.append(z3_path)

import argparse, subprocess, z3, time
from datetime import datetime

# proof mode must be enabled before any expressions are created
z3.set_param(proof=True)
z3.set_param(model=True)

# Create the script args parser
parser = argparse.ArgumentParser(description="A script to process problem and result files")

# Add optional arguments with default values
parser.add_argument('--pf', default='problem.smt2', help='Path to the problem file')
parser.add_argument('--rf', default='result.smt2', help='Path to the result file')
parser.add_argument('--max_depth', default=100, help='Amount of iteration for SPACER to find the invariant')
parser.add_argument('--s', default=True, help='Indicate whether SPACER will find solution for rewrittencode')


ascii_art = r"""
███╗░░░███╗░█████╗░░██████╗░██╗░█████╗░██╗░░██╗███████╗░█████╗░██████╗░███╗░░░███╗
████╗░████║██╔══██╗██╔════╝░██║██╔══██╗╚██╗██╔╝██╔════╝██╔══██╗██╔══██╗████╗░████║
██╔████╔██║███████║██║░░██╗░██║██║░░╚═╝░╚███╔╝░█████╗░░██║░░██║██████╔╝██╔████╔██║
██║╚██╔╝██║██╔══██║██║░░╚██╗██║██║░░██╗░██╔██╗░██╔══╝░░██║░░██║██╔══██╗██║╚██╔╝██║
██║░╚═╝░██║██║░░██║╚██████╔╝██║╚█████╔╝██╔╝╚██╗██║░░░░░╚█████╔╝██║░░██║██║░╚═╝░██║
╚═╝░░░░░╚═╝╚═╝░░╚═╝░╚═════╝░╚═╝░╚════╝░╚═╝░░╚═╝╚═╝░░░░░░╚════╝░╚═╝░░╚═╝╚═╝░░░░░╚═╝
"""
print(ascii_art)

#---- Helper functions -----------

Z = z3.IntSort()
B = z3.BoolSort()
start_time = time.time()


def get_current_time():
    """Get the current time and format it"""
    return datetime.now().strftime("%H:%M:%S")

def t_log(log):
    curr_time = get_current_time()
    print(f"{curr_time} | ----- {log} ----- \n")

def read_file(problem_file='prblm.smt2'):
    with open(problem_file, 'r') as file:
        code = file.read()
    return code 

def expand_quant(fml):
    """Expand quantifier into Quantifier, Variables, and Body."""
    if z3.is_quantifier(fml):
        gnd_vars = [z3.Const(fml.var_name(i), fml.var_sort(i)) for i in range(fml.num_vars())]
        gnd_body = z3.substitute_vars(fml.body(), *reversed(gnd_vars))
        quant = z3.Exists if fml.is_exists() else z3.ForAll
        return quant, gnd_vars, gnd_body
    else:
        return (lambda x, y: y), [], fml
    
def apply_to_each_expr(fml, fn, *args, **kwargs):
    """Apply given function to every sub-expression of a formula."""
    if fn(fml, *args, **kwargs):
        for child in fml.children():
            apply_to_each_expr(child, fn, *args, **kwargs)

#---- Initial problem parser functions -----------

def setup_fixedpoint(max_depth):
    fp = z3.Fixedpoint()
    fp.set('spacer.max_level', max_depth)
    return fp

def parse_queries(fp, code):
    queries = fp.parse_string(code)
    assert len(queries) == 1
    return queries

def extract_rules(fp):
    return fp.get_rules()

#---- Magic number finders -----------

def is_magic_num(v):
    return z3.is_int_value(v) and v.as_long() != 0

def has_comparison_operator(expr):
    comparison_ops = [z3.is_lt, z3.is_le, z3.is_gt, z3.is_ge, z3.is_eq, z3.is_distinct]
    return any(op(expr) for op in comparison_ops)

def has_div_or_mod_operator(expr):
    div_ops = [z3.is_div, z3.is_idiv, z3.is_mod]
    return any(op(expr) for op in div_ops)

def has_magic_num_child(expr):
    return any(is_magic_num(child) for child in expr.children())

def find_magic_root(expr):
    """Magic root means if expr has comparison operator and at least one of the children is a number"""
    return has_comparison_operator(expr) and has_magic_num_child(expr)


def find_magic_in_gnd_rule(rule):
    myset = set()

    def find_magic(x, found):
        if has_div_or_mod_operator(x):
            return False
        if find_magic_root(x): 
            for arg in x.children():
                if is_magic_num(arg):
                    found.add(arg)
            return False
        else:
            return True
        
    apply_to_each_expr(rule, find_magic, found=myset)
    return myset

def find_magic_in_rule(rule):
    _, _, b = expand_quant(rule)
    return find_magic_in_gnd_rule(b)

def find_magic_values(rules):
    return list(set().union(*map(find_magic_in_rule, rules)))

#---- Problem rewrite functions -----------

def prepare_substitution(values, prefix):
    values_consts = [z3.IntVal(val) for val in values]
    values_vars = [z3.Int(f"{prefix}{val}") for val in values]
    return values_vars, [*zip(values_consts, values_vars)]

def apply_substitution(rules, substitutions):
    return [z3.substitute(rule, substitutions) for rule in rules]

def reverse_pairs(lst):
    return [(y, x) for x, y in lst]

def substitute_with_exceptions(rule, substitutions):
    rule_quant, rule_args, rule_body = expand_quant(rule)
    reversed_subs = reverse_pairs(substitutions)
    new_sub_rule = set()
    
    def custom_substituter(expr, found):
        if has_div_or_mod_operator(expr):
            sub_expr = z3.substitute(expr, reversed_subs)
            found.add((expr, sub_expr))
            return False
        else:
            return True
            
    apply_to_each_expr(rule_body, custom_substituter, found=new_sub_rule)
    substituted_rule_body = z3.substitute(rule_body, new_sub_rule)
    substituted_rule = rule_quant(rule_args, substituted_rule_body)
    return substituted_rule

def int_2_var(rules, substitutions):
    subs_rules = apply_substitution(rules, substitutions)
    new_rules = [substitute_with_exceptions(rule, substitutions) for rule in subs_rules]
    return new_rules
    

def apply_custom_substitution(rules, substitutions):
    first_rule = [rules[0]]
    new_rules = int_2_var(rules[1:], substitutions)
    return first_rule + new_rules

def generate_additional_conditions(substitutions):
    return [(sub_var == sub_val) for sub_val, sub_var in substitutions]

def implies_and_way(rule_body, additional_conditions):
    assert(z3.is_implies(rule_body))
    assert(z3.is_and(rule_body.arg(0)))
    return z3.And(*rule_body.arg(0).children(), *additional_conditions)

def implies_way(rule_body, additional_conditions):
    assert(z3.is_implies(rule_body))
    assert not z3.is_and(rule_body.arg(0))
    return z3.And(rule_body.arg(0), *additional_conditions)

def clear_inv_way(additional_conditions):
    return z3.And(*additional_conditions)
    
def construct_first_rule(rule_body, additional_conditions):
    if z3.is_implies(rule_body):
        if z3.is_and(rule_body.arg(0)):
            return rule_body.arg(1), implies_and_way(rule_body, additional_conditions)
        else:
            return rule_body.arg(1), implies_way(rule_body, additional_conditions)
    else:
        return rule_body, clear_inv_way(additional_conditions)


def process_first_rule(rules, add_rules, substitutions):
    _, _, rule_body = expand_quant(rules[0])
    # additional_conditions = generate_additional_conditions(substitutions)   
    additional_conditions = add_rules
    # t_log(f"additional_conditions: {additional_conditions}") 
    rule_head, rule_tail = construct_first_rule(rule_body, additional_conditions)
    rules[0] = z3.Implies(rule_tail, rule_head)
    return rules

def create_new_rules(rules, magic_values_vars):
    return [*map(lambda rule: mk_new_rule(rule, magic_values_vars), rules)]

def create_new_vars(rules):
    return list(set().union(*map(mk_rule_vars, rules)))

#---- GCD based rules

def gcd_based_rules(magic_values):
    int_magic_values = [int(m_int.as_long()) for m_int in magic_values]
    gcd, diff, magic_values, gcd_rules = param_finder(int_magic_values)
    gcd_range_rules, gcd_z3_var = gcd_substituition(gcd)
    # upd_gcd_rules = int_2_var(gcd_rules, gcd_substitution)
    # gcd_rules = gcd_range_rules + gcd_rules
    # t_log(f"upd_gcd_rules: {gcd_rules}")
    return diff, magic_values, gcd_rules, gcd_range_rules, gcd_z3_var

#----

def process_rules_and_queries(code, max_depth):
    fp = setup_fixedpoint(max_depth)
    queries = parse_queries(fp, code)
    rules = extract_rules(fp)
    magic_values = find_magic_values(rules[1:])

    diff, magic_values, gcd_rules, gcd_range_rules, gcd_z3_var = gcd_based_rules(magic_values)
    magic_values_vars, substitutions = prepare_substitution(magic_values+diff, "K")
    magic_values_vars = magic_values_vars + [gcd_z3_var]

    subs_rules = int_2_var(rules, substitutions)
    
    gcd_rules = int_2_var(gcd_rules, substitutions)
    gcd_rules = gcd_range_rules+gcd_rules

    new_rules = process_first_rule(subs_rules, gcd_rules, substitutions)
    return new_rules, queries, magic_values_vars

#---- New invariant creation -----------

def find_invs(gnd_rule_body, inv_name='inv'):
    found = set()

    def _is_inv_term(e, found):
        if e.decl().name().startswith(inv_name):
            found.add(e)
            return False
        return True

    apply_to_each_expr(gnd_rule_body, _is_inv_term, found=found)
    return found

def append_sorts(inv_term, new_vars):
    inv2_sorts = [inv_term.decl().domain(i) for i in range(inv_term.decl().arity())]
    for v in new_vars:
        inv2_sorts.append(v.sort())
    inv2_sorts.append(B)
    return inv2_sorts

def mk_inv2(inv_term, new_vars=[]):
    inv2_sorts = append_sorts(inv_term, new_vars)
    inv2_fdecl = z3.Function("inv2", *inv2_sorts)
    inv2_args = inv_term.children() + new_vars
    inv2_term = inv2_fdecl(*inv2_args)
    return inv2_term, inv2_fdecl

def mk_rule_vars(rule):
    _, rule_vars, _ = expand_quant(rule)
    return rule_vars

def generate_rule_substitutions(rule_body, new_vars):
    subs = list()
    inv_terms = find_invs(rule_body)
    for inv_term in inv_terms:
        inv2_term, _ = mk_inv2(inv_term, new_vars)
        subs.append((inv_term, inv2_term))
    return subs

def flatten(lst):
    result = []
    for i in lst:
        if isinstance(i, list):
            result.extend(flatten(i))
        else:
            result.append(i)
    return result


def get_inv_instance(rule):
    def inve(rule_body):
        inv_list = list()
        inv_terms = find_invs(rule_body)
        for inv_term in inv_terms:
            _, inv2 = mk_inv2(inv_term)
            inv_list.append(inv2)
        return inv_list

    _, _, rule_body = expand_quant(rule)
    inv_list = inve(rule_body)
    return inv_list

def mk_new_rule(rule, values_vars):
    _, _, rule_body = expand_quant(rule)
    subs = generate_rule_substitutions(rule_body, values_vars)
    new_body = z3.substitute(rule_body, subs)
    return new_body

#---- Main rewriter process -----------

def set_fixedpoint(new_rules, new_vars, additional_vars):
    fp_new = z3.Fixedpoint()
    invs = flatten([*map(get_inv_instance, new_rules)])
    inv2 = invs[0]
    fp_new.register_relation(inv2)
    fp_new.register_relation(z3.Function('fail', B))
    fp_new.declare_var(*new_vars)
    fp_new.declare_var(*additional_vars)
    for new_rule in new_rules:
        fp_new.add_rule(new_rule)
    return fp_new

def rewritten_result(fp_new, queries):
    return fp_new.to_string(queries)

def write_to_console(fp_new, queries):
    t_log("Rewritten code section")
    print(rewritten_result(fp_new, queries))

def write_to_file(fp_new, queries, filename='res.smt2'):
    with open(filename, 'w') as f:
        print(rewritten_result(fp_new, queries), file=f)

# Result section

def extract_required_parts(logs):
    logs_list = logs.split('\n')  # Splits the logs into lines
    required_parts = []

    for log in logs_list:
        if log.startswith("(define-fun inv"):
            required_parts.append(log)
        elif len(required_parts) > 0 and not log.startswith("expand:"):
            # continue appending lines if it's part of the 'define-fun' block
            required_parts.append(log)

    return '\n'.join(required_parts)

def push_subprocess(result_file, max_depth):
    cmd = [
        z3_eval_path + "/z3",
        "fp.spacer.max_level="+ str(max_depth),
        "fp.spacer.global=true",
        result_file,
        "-v:1"
        # fp.xform.inline_eager=false 
        # fp.xform.inline_linear=false
    ]

    loader = Loader("Finding an invariant for the rewritten code...", "\n").start()

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, logs = proc.communicate()
    output = output.decode('utf-8').upper()
    logs = logs.decode('utf-8')

    loader.stop()
    t_log("Result section")
    
    if "UNSAT" in output:
        result = "SAT"
        inv = extract_required_parts(logs)
        print(f"Output: {result}")
        print(f"Invariant: \n{inv}")
        return result, inv
    elif "SAT" in output:
        result = "UNSAT"
        print(f"Output: {result}")
        print(f"Logs: \n{logs}")
        return result, logs        
    else:
        print(f"Output: {output}")
        print(f"Errors: \n{logs}")
        return output, logs        

def dummy_bool_parser(s):
    if s == 'False':
        return False
    else:
        return True

def parse_cmd_args():
    program_args = parser.parse_args()

    problem_file = str(program_args.pf)
    result_file = str(program_args.rf)
    is_solving_on = dummy_bool_parser(program_args.s)
    max_depth = int(program_args.max_depth)

    t_log(f"CMD params: {vars(program_args)}")

    return problem_file, result_file, max_depth, is_solving_on

def extract_name_from_path(path):
    return os.path.basename(path)

def main():
    problem_file, result_file, max_depth, is_solving_on = parse_cmd_args()
    result_file = f"/home/ekvashyn/Code/magicXform/magicXform/tmp/{result_file}"

    code = read_file(problem_file)

    rules, queries, magic_values_vars = process_rules_and_queries(code, max_depth)

    new_rules = create_new_rules(rules, magic_values_vars)
    new_vars = create_new_vars(rules)
    
    fp_new = set_fixedpoint(new_rules, new_vars, magic_values_vars)

    fp_rules = fp_new.get_rules()
    fp_rules.push(z3.Implies(queries[0], z3.BoolVal(False)))

    write_to_console(fp_new, queries)
    write_to_file(fp_new, queries, result_file)
    
    if is_solving_on:
        output, _ = push_subprocess(result_file, max_depth)
        result_file_name = extract_name_from_path(problem_file)
        out_time = time.time() - start_time
        out_time = round(out_time, 2)
        result_file = f"../results/{output}/{out_time}-{result_file_name}"
        

        write_to_file(fp_new, queries, result_file)
        t_log(f"Program took {out_time}s to run")
    
    

if __name__ == '__main__':
    main()