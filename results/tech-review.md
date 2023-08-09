# Techniques review 

> The road will be mastered by walking (c)

As an applied math student and visitor researcher, I was onboarded for exploring the program verification field. My expedition began with learning various techniques and approaches to solving problems, utilizing both forward, and backward inductions and many more distinct techniques. But like any person, we all have something in life that radically changes it or brings something new into it...

### The Challenge:

The initiation of my exploration was guided by a paper that shed light on a comparative study of the performance of Spacer and several other solvers, using a collection of 54 smt2 problem files. In accordance with the observations deduced from the paper, ImplCheck outshined all other tools by solving 44 challenges. On the contrary, Spacer could efficiently address only 19 out of the 54 tasks. My ever-inquisitive mind took this as a challenge. "I learned inductions and things. Of course, I should be able to solve them!" I said. "It would be interesting to find the problem in this problem and teach Spacer how to get through these fancy challenges he couldn't solve for any reason". I embarked on a mission to augment the number of problems Spacer could solve.

### The Idea:

In the process of unraveling the cause of Spacer's underperformance, I discovered certain instances which Spacer was unable to solve. A pattern began to emerge, as it seemed Spacer was specifically confounded by numbers. To address this issue, I devised a strategy of substituting numbers founded in scopes that have comparison operators with variables of identical value. Following several attempts, my perseverance bore fruit and this solution proved to be effective. One after another, the unsolved instances started showing solved results.

```
Example 1

...

(rule (=> (and (= x0 0) (= y0 5000))
    (inv x0 y0)))

(rule (=> (and
        (inv x0 y0)
        (= x1 (+ x0 1))
        (= y1 (ite (>= x0 5000) (+ y0 1) y0)))
    (inv x1 y1)))

(rule (=> (and (inv x0 y0) (= x0 10000)
    (not (= y0 x0))) fail))

...

Magic numbers are 5000 and 10000. Let's make the substitution. For this, we will substitute numbers as variables K5000 and K10000 and initialize them in the init (first) rule.

...

(rule (=> (and (= x0 0) (= y0 5000) (= 10000 K10000) (= 5000 K5000))
    (inv x0 y0 A B)))

(rule (=> (and
        (inv x0 y0 A B)
        (= x1 (+ x0 1))
        (= y1 (ite (>= x0 K5000) (+ y0 1) y0)))
    (inv x1 y1 A B)))

(rule (=> (and (inv x0 y0 A B) (= x0 K10000)
    (not (= y0 x0))) fail))

...
```

The idea of substitution wasn't difficult. Actually, it wasn't even new for me, because I recognized a software development antipattern "Magic numbers" and decided to implement it and make a new tool, that could refactor initial code without those numbers, at least explicitly. The newly created tool got named "magicXform".

### The Triumph:

The implemented technique in the tool ran systematically across all 54 challenges. As a result, Spacer's performance soared from initially solving 19 challenges to successfully addressing a count of 32 obstacles, which I think isn't a bad result.

## magicXform

### Why does this even work?

As mentioned earlier, I realized that Spacer is getting confused with numbers. When I tried different methods, I provided variables instead of magic numbers. This worked for the z3 homemade prover, which returned the invariant to me faster and with fewer magic number restrictions. I decided to use a similar strategy for rewriting CHC benchmarks so Spacer couldn't see the numbers.

Next, we will try to understand how the replacement of numbers affects Spacer and why it began to solve problems. For clarity, consider a simple example, which we have already seen. The full code is below:

###### Original benchmark locates in passed-challenges/s_split_01.smt2
```
(declare-rel inv (Int Int))
(declare-var x0 Int)
(declare-var x1 Int)
(declare-var y0 Int)
(declare-var y1 Int)

(declare-rel fail ())

(rule (=> (and (= x0 0) (= y0 5000))
    (inv x0 y0)))

(rule (=> (and
        (inv x0 y0)
        (= x1 (+ x0 1))
        (= y1 (ite (>= x0 5000) (+ y0 1) y0)))
    (inv x1 y1)))

(rule (=> (and (inv x0 y0) (= x0 10000)
    (not (= y0 x0))) fail))

(query fail)
```

Let's look inside the Spacer trace file and see what is going on. Commence from the first level. Here we can behold that Spacer instantly put numbers in the lemma it has learned.

###### Look over trace file located in results/logs/s_split_1.log
```
* LEVEL 1

** expand-pob: inv level: 0 depth: 0 exprID: 290 pobID: 1
(and (= x 10000) (< y 10000))

** add-lemma: 0 exprID: 486 pobID: 290
inv
(< x 10000)
```

The second point to consider is how the tool recognizes different lemmas that incorporate something akin to a "magic number". However, the twist is that this number may undergo a subtle transformation such as an increment or decrement by 1. This creates a direct effect on the number, replacing what was once a unique expression with this transformed number. For instance, an expression like `(x - 1)` might be replaced with `9999`. Here's a snippet from the trace that demonstrates this concept:
  
###### Look over trace file located in results/logs/s_split_1.log
```
* LEVEL 3

** expand-pob: inv level: 2 depth: 0 exprID: 290 pobID: 1
(and (= x 10000) (< y 10000))

** expand-pob: inv level: 1 depth: 0 exprID: 693 pobID: 290
(and (>= x 5000) (< y 9999) (= x 9999))

** add-lemma: 1 exprID: 1010 pobID: 693
inv
(< x 2)
```

Another reason leans in simply Spacer's brute force when he tries to find a relation between numbers. It takes a lot of operations and does not necessarily help find the invariant, because if the number represented in the instance is high (let's say N) it will make approximately N attempts to find correct invariant relations. This point is illustrated in the snippet below:

###### Look over trace file located in results/logs/s_split_1.log
```
* LEVEL 69

** expand-pob: inv level: 68 depth: 0 exprID: 1369 pobID: 1
(and (= x 10000) (> y 10000))

** expand-pob: inv level: 67 depth: 0 exprID: 9376 pobID: 1369
(and (>= x 5000) (= x 9999) (> y 9999))

** expand-pob: inv level: 66 depth: 0 exprID: 10095 pobID: 9376
(and (>= x 5000) (> y 9998) (= x 9998))

** expand-pob: inv level: 65 depth: 0 exprID: 10114 pobID: 10095
(and (>= x 5000) (> y 9997) (= x 9997))

...

** expand-pob: inv level: 22 depth: 0 exprID: 339197 pobID: 184729
(and (>= x 5000) (> y 9954) (= x 9954))

** expand-pob: inv level: 21 depth: 0 exprID: 339343 pobID: 339197
(and (>= x 5000) (> y 9953) (= x 9953))

** add-lemma: 21 exprID: 194970 pobID: 339343
inv
(< x 9953)

** expand-pob: inv level: 14 depth: 0 exprID: 340006 pobID: 1
(and (> y 9953) (= x 9953))

** expand-pob: inv level: 14 depth: 0 exprID: 339694 pobID: 1
(> y 9953)

** add-lemma: 14 exprID: 339990 pobID: 339694
inv
(< y 5017)
```

After this point reading the rest of the trace file turns into a nightmare:

###### Look over trace file located in results/logs/s_split_1.log
```
** expand-pob: inv level: 25 depth: 14 exprID: 347795 pobID: 347872
(and (>= x 5000)
     (>= x 4999)
     (<= x (+ y (- 1)))
     (<= x 9969)
     (>= x 9951))

** add-lemma: 25 exprID: 348463 pobID: 347795
inv
(or (> x (+ y (- 1))) (> x 9969) (< x 9951))

** expand-pob: inv level: 26 depth: 14 exprID: 347872 pobID: 347638
(and (>= x 5000)
     (<= x (+ y (- 1)))
     (<= x 9970)
     (>= x 9952))

** add-lemma: 26 exprID: 348218 pobID: 347872
inv
(or (> x (+ y (- 1))) (> x 9970) (< x 9952))

** expand-pob: inv SUBS level: 27 depth: 14 exprID: 347638 pobID: 1
(and (<= x (+ y (- 1))) (<= x 9971) (>= x 9953))

** add-lemma: 27 exprID: 347556 pobID: 347638
inv
(or (> x (+ y (- 1))) (> x 9971) (< x 9953))

** expand-pob: inv SUBS level: 28 depth: 4 exprID: 345849 pobID: 1
(and (<= x (+ y (- 1))) (<= x 9971) (>= x 9956))

** add-lemma: 28 exprID: 345896 pobID: 345849
inv
(or (> x (+ y (- 1))) (> x 9971) (< x 9956))

** expand-pob: inv SUBS level: 29 depth: 5 exprID: 345849 pobID: 1
(and (<= x (+ y (- 1))) (<= x 9971) (>= x 9956))

** expand-pob: inv level: 28 depth: 5 exprID: 346099 pobID: 345849
(and (>= x 5000)
     (<= x (+ y (- 1)))
     (<= x 9970)
     (>= x 9955))

** add-lemma: 28 exprID: 347573 pobID: 346099
inv
(or (> x (+ y (- 1))) (> x 9970) (< x 9955))

** expand-pob: inv SUBS level: 29 depth: 5 exprID: 345849 pobID: 1
(and (<= x (+ y (- 1))) (<= x 9971) (>= x 9956))

** add-lemma: 29 exprID: 345896 pobID: 345849
inv
(or (> x (+ y (- 1))) (> x 9971) (< x 9956))

** expand-pob: inv SUBS level: 30 depth: 6 exprID: 345849 pobID: 1
(and (<= x (+ y (- 1))) (<= x 9971) (>= x 9956))

** expand-pob: inv level: 29 depth: 6 exprID: 346099 pobID: 345849
(and (>= x 5000)
     (<= x (+ y (- 1)))
     (<= x 9970)
     (>= x 9955))

** expand-pob: inv level: 28 depth: 6 exprID: 343763 pobID: 346099
(and (>= x 5000)
     (>= x 4999)
     (<= x (+ y (- 1)))
     (<= x 9969)
     (>= x 9954))
```

### Bottom Line on Current Spacer's Numerical Issues

To summarize, this part of the review highlighted how Spacer struggles with 'magic numbers' and performs better with variables instead, as observed in comparisons with a custom z3 solver. Spacer transforms these numbers by slightly adjusting them, which can lead to inefficiencies in finding the invariant, especially when dealing with large numbers. Spacer also tends to use brute force to find relationships between numbers, making 'N' attempts for a number 'N', indicating a potential area for performance optimization. The next step of the investigation will focus on studying the effect of replacing magic numbers with variables on Spacer's efficiency.

---

```
* LEVEL 1

** expand-pob: query!0 level: 1 depth: 0 exprID: 1 pobID: none
true

** expand-pob: inv2 level: 0 depth: 0 exprID: 328 pobID: 1
(and (= K10000 x) (< x y))

** add-lemma: 0 exprID: 708 pobID: 328
inv2
(< x K10000)
```
