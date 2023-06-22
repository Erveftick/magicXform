import sys
import argparse
import z3
sys.path.append("/home/ekvashyn/Code/spacer-on-jupyter/src")

from spacer_tutorial import *
from chctools import chcmodel, horndb

# proof mode must be enabled before any expressions are created
z3.set_param(proof=True)
z3.set_param(model=True)


# Create the script args parser
parser = argparse.ArgumentParser(description="A script to process problem and result files")

# Add optional arguments with default values
parser.add_argument('--pf', default='problem.smt2', help='Path to the problem file')
parser.add_argument('--rf', default='result.smt2', help='Path to the result file')


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

def setup_fixedpoint():
    fp = z3.Fixedpoint()
    fp.set('spacer.max_level', 40)
    return fp

def parse_queries(fp, code):
    queries = fp.parse_string(code)
    assert len(queries) == 1
    fp.query(queries[0])
    return queries

def extract_rules(fp):
    return fp.get_rules()

#---- Magic number finders -----------


def is_magic_num(v):
    return z3.is_int_value(v) and v.as_long() != 0

def has_comparison_operator(expr):
    comparison_ops = [z3.is_lt, z3.is_le, z3.is_gt, z3.is_ge, z3.is_eq, z3.is_distinct]
    return any(op(expr) for op in comparison_ops)

def find_magic_in_gnd_rule(rule):
    myset = set()

    def find_magic(x, found):
        if has_comparison_operator(x): 
            for arg in [x.arg(0), x.arg(1)]:
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

def prepare_substitution(values):
    values_consts = [z3.IntVal(val) for val in values]
    values_vars = [z3.Int(f"K{val}") for val in values]
    values_vars = list(reversed(values_vars))
    return values_vars, [*zip(values_consts, values_vars)]

def apply_substitution(rules, substitutions):
    return [z3.substitute(rule, substitutions) for rule in rules]

def generate_additional_conditions(substitutions):
    return [(sub_var == sub_val) for sub_val, sub_var in substitutions]

def process_first_rule(rules, substitutions):
    _, _, rule_body = expand_quant(rules[0])
    assert(z3.is_implies(rule_body))
    assert(z3.is_and(rule_body.arg(0)))
   
    additional_conditions = generate_additional_conditions(substitutions)
    upd_first_rule_tail = z3.And(*rule_body.arg(0).children(), *additional_conditions)
    rules[0] = z3.Implies(upd_first_rule_tail, rule_body.arg(1))
    return rules

def create_new_rules(rules, magic_values_vars):
    return [*map(lambda rule: mk_new_rule(rule, magic_values_vars), rules)]

def create_new_vars(rules):
    return list(set().union(*map(mk_rule_vars, rules)))

def process_rules_and_queries(code):
    fp = setup_fixedpoint()
    queries = parse_queries(fp, code)
    rules = extract_rules(fp)
    magic_values = find_magic_values(rules)
    magic_values_vars, substitutions = prepare_substitution(magic_values)
    subs_rules = apply_substitution(rules, substitutions)
    new_rules = process_first_rule(subs_rules, substitutions)
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
    print("----- Rewritten code section -----\n")
    print(rewritten_result(fp_new, queries))

def write_to_file(fp_new, queries, filename='res.smt2'):
    with open(filename, 'w') as f:
        print(rewritten_result(fp_new, queries), file=f)

def process_horn(sh_db, fp_rules):
    res, answer = solve_horn(fp_rules, max_unfold=40)
    s_res = str(res)

    print("----- Result section -----\n")
    print(f"Result: {s_res.upper()}")
    if res == z3.sat:
        print(f"Model valid?: {chcmodel.ModelValidator(sh_db, answer).validate()}")
        print(f"Answer: \n {answer.sexpr()}")

def main():
    # Parse the cmd arguments
    program_args = parser.parse_args()

    problem_file = str(program_args.pf)
    result_file = str(program_args.rf)

    code = read_file(problem_file)

    rules, queries, magic_values_vars = process_rules_and_queries(code)

    new_rules = create_new_rules(rules, magic_values_vars)
    new_vars = create_new_vars(rules)
    
    fp_new = set_fixedpoint(new_rules, new_vars, magic_values_vars)

    write_to_console(fp_new, queries)
    write_to_file(fp_new, queries, result_file)

    fp_rules = fp_new.get_rules()
    fp_rules.push(z3.Implies(queries[0], z3.BoolVal(False)))

    sh_db = horndb.HornClauseDb("prblm")
    sh_db.load_from_fp(fp_new, queries)
    process_horn(sh_db, fp_rules)
    

if __name__ == '__main__':
    main()