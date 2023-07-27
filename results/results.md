# Tool results and comparasion

Here will be stored perfomance information about each of the versions of the tool. 

## **version 0.1.0**

### Max_depth correlation

Tool represent foolowing data that corresponds to max_depth option

| max_depth | challenges                    |
|-----------|-------------------------------|
| 40        | 1,2,3,4,5,6,7,8,13,17,21,26,31,32,34,35,36,37,38,46,56 |
| 100       | 6,12,23,29,43,55              |
| 300       | 28,44,54                      |

### Comparison with GSpacer

Set of the challenges that solves one tool but doesn't solves another.

| GSpacer | magicXform |
|---------|------------|
|  19, 39 | 3, 8, 12, 13, 17, 21, 28, 31, 32, 43, 44, 54, 55, 56 |

### Unsolved problems review

**s_split_19.smt2** - substituted number cause stucking in the rewritten code. Original problem was solved by GSpacer in less than a second

**s_split_47.smt2** - problem contains only one magic number according to rules of this ver of the tool. Number 777 can't be substituted because problem becomes more difficult (LIA -> NIA)


### Conclusion

To get following table run *analytics.py*

| Challenge type | Amount | Challenges |
|---|---|---|
| SAT resolved | 32 | 1, 2, 3, 4, 5, 6, 7, 8, 12, 13, 17, 18, 21, 23, 26, 28, 29, 31, 32, 34, 35, 36, 37, 38, 41, 42, 43, 44, 46, 54, 55, 56 |
| Diff: magicXform | 15| 3, 8, 12, 13, 17, 21, 28, 31, 32, 41, 43, 44, 54, 55, 56 |
| Diff: GSpacer | 2| 19, 39 |

---

Problematic tasks that don't contain div or mod operations: 19, 30, 45, 47, 48, 49, 51, 52, 57
Problems located in **challenges/review** folder

<!-- s_split_19.smt

s_split_30.smt

s_split_45.smt

s_split_47.smt

s_split_48.smt

s_split_49.smt

s_split_51.smt

s_split_52.smt

s_split_57.smt -->

Here represented a table with my attempts to find a universal approach for each of the problems but failed

In the path cell represented amount of time taken for getting the solution

|    Problem    | GCD* vanilla | GCD with opts** | GCD arith |
|---------------|--------------|-----------------|-----------|
|   res_48_4    | stuck        |         -       |      -    |
|   res_49_1    | -            |         -       |      -    |
|   res_49_2    | + (23s)      |     + (17s)     | + (24.5s) |
|   res_49      | -            |         +       |      -    |
|   res_49_bwd  | stuck        |     stuck       |   stuck   |
|   51-99.93s   | + (110s)     |         -       |   + (90s) |

\* GCD idea - Main idea is to find a GCD number among all the magic numbers. Then this value I put into the additional rule and implied invariant I conjoin to the rules where it's necessary (where this variable is used)

\** with options means *fp.xform.inline_eager=false* and *fp.xform.inline_linear=false*