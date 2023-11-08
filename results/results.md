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

## **version 0.1.1**

The version provides a magicXform with parametrization idea. We ran script among all challenges that we have and got following results:

|     Problem     |   Time   |
|-----------------|----------|
| s_split_01.smt2 | 0.62s |
| s_split_02.smt2 | 0.18s |
| s_split_06.smt2 | 0.48s |
| s_split_07.smt2 | 0.23s |
| s_split_08.smt2 | 0.60s |
| s_split_10.smt2 | 14.75s |
| s_split_11.smt2 | 0.61s |
| s_split_17.smt2 | 0.21s |
| s_split_19.smt2 | 0.18s |
| s_split_24.smt2 | 0.62s |
| s_split_37.smt2 | 0.27s |
| s_split_38.smt2 | 0.23s |
| s_split_39.smt2 | 0.20s |
| s_split_42.smt2 | 1.30s |
| s_split_43.smt2 | 0.57s |
| s_split_44.smt2 | 2.14s |
| s_split_46.smt2 | 2.01s |
| s_split_48.smt2 | 147.06s |
| s_split_49.smt2 | 10.67s |
| s_split_51.smt2 | 1.59s |
| s_split_54.smt2 | 3.13s |
| s_split_57.smt2 | 10.11s |


However we had a problem with correct transformation, because some of the instances returned UNSAT, which means that transformed program has bug so
couldn't find the invariant. Below locates table with such problems:

|     Problem     |
|-----------------|
| s_split_32.smt2 |
| s_split_16.smt2 |
| s_split_41.smt2 |
| s_split_55.smt2 |
| s_split_30.smt2 |
| s_split_40.smt2 |
| s_split_25.smt2 |
| s_split_12.smt2 |
| s_split_20.smt2 |
| s_split_22.smt2 |
| s_split_29.smt2 |
| s_split_04.smt2 |
| s_split_18.smt2 |
| s_split_34.smt2 |

Anyways, if we will apply both techniques from the version 0.1.0 and 0.1.0 we will have 41/58 solved chanllenges. The res ult shows us that this ideas can improve Spacer effectiveness in 2.15 times than it was before.

## Comparative tables

### Version 0.1.0

|     Problem     |   Time   |
|-----------------|----------|
| s_split_01.smt2 | 1.81s |
| s_split_02.smt2 | 0.43s |
| s_split_03.smt2 | 0.39s |
| s_split_04.smt2 | 0.51s |
| s_split_05.smt2 | 0.42s |
| s_split_07.smt2 | 0.55s |
| s_split_08.smt2 | 3.29s |
| s_split_12.smt2 | 6.31s |
| s_split_13.smt2 | 0.35s |
| s_split_17.smt2 | 0.38s |
| s_split_18.smt2 | 7.74s |
| s_split_21.smt2 | 0.57s |
| s_split_23.smt2 | 0.23s |
| s_split_26.smt2 | 260.44s |
| s_split_28.smt2 | 218.21s |
| s_split_29.smt2 | 164.11s |
| s_split_31.smt2 | 0.38s |
| s_split_32.smt2 | 69.53s |
| s_split_34.smt2 | 0.35s |
| s_split_35.smt2 | 0.27s |
| s_split_36.smt2 | 0.14s |
| s_split_37.smt2 | 0.90s |
| s_split_38.smt2 | 0.30s |
| s_split_41.smt2 | 56.40s |
| s_split_42.smt2 | 0.54s |
| s_split_43.smt2 | 7.19s |
| s_split_46.smt2 | 76.94s |
| s_split_54.smt2 | 278.44s |
| s_split_55.smt2 | 4.95s |
| s_split_56.smt2 | 0.35s |

Total: 30

### version 0.1.1

#### SAT

|     Problem     |   Time   |
|-----------------|----------|
| s_split_01.smt2 | 0.67s |
| s_split_02.smt2 | 0.22s |
| s_split_03.smt2 | 0.41s |
| s_split_04.smt2 | 0.46s |
| s_split_05.smt2 | 0.42s |
| s_split_06.smt2 | 0.51s |
| s_split_07.smt2 | 0.69s |
| s_split_08.smt2 | 3.21s |
| s_split_10.smt2 | 22.70s |
| s_split_12.smt2 | 13.43s |
| s_split_13.smt2 | 0.63s |
| s_split_17.smt2 | 0.36s |
| s_split_18.smt2 | 7.88s |
| s_split_21.smt2 | 0.60s |
| s_split_23.smt2 | 0.26s |
| s_split_24.smt2 | 0.71s |
| s_split_26.smt2 | 247.98s |
| s_split_28.smt2 | 197.71s |
| s_split_31.smt2 | 0.35s |
| s_split_32.smt2 | 67.32s |
| s_split_34.smt2 | 0.19s |
| s_split_35.smt2 | 0.31s |
| s_split_36.smt2 | 0.15s |
| s_split_37.smt2 | 0.30s |
| s_split_38.smt2 | 0.27s |
| s_split_42.smt2 | 2.02s |
| s_split_43.smt2 | 0.74s |
| s_split_44.smt2 | 2.88s |
| s_split_46.smt2 | 3.12s |
| s_split_48.smt2 | 264.86s |
| s_split_49.smt2 | 18.95s |
| s_split_51.smt2 | 2.00s |
| s_split_54.smt2 | 4.25s |
| s_split_56.smt2 | 0.41s |
| s_split_57.smt2 | 16.91s |

Total: 35


#### UNSAT

|     Problem     |   Time   |
|-----------------|----------|
| s_split_16.smt2 | 0.19s |
| s_split_20.smt2 | 0.21s |
| s_split_22.smt2 | 0.14s |
| s_split_25.smt2 | 0.17s |
| s_split_29.smt2 | 0.20s |
| s_split_30.smt2 | 0.16s |
| s_split_40.smt2 | 1.15s |
| s_split_41.smt2 | 0.20s |
| s_split_55.smt2 | 0.21s |

Total: 9