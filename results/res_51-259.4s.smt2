(declare-rel fail ())
(declare-rel inv2 (Int Int Int Int Int Int Int))
(declare-var A Int)
(declare-var B Int)
(declare-var C Int)
(declare-var D Int)
(declare-var E Int)
(declare-var F Int)
(declare-var G Int)
(declare-var H Int)
(declare-var I Int)
(declare-var N Int)
(rule (=> (and (= G 0) (= D B) (= I A) (> N 0) (<= N 3333) (= (* 3 N) C) (= N B) (= (* N 2) A))
    (inv2 G D I C B A N)))
(rule (let ((a!1 (and (inv2 G D I C B A N)
                (= E (+ G 1))
                (= H (ite (< G B) D (+ D 1)))
                (= F (ite (>= D A) (+ I 1) I)))))
  (=> a!1 (inv2 E H F C B A N))))
(rule (=> (and (inv2 G D I C B A N) (= G C) (not (= I G))) fail))
(query fail)

