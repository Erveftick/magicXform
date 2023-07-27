
(declare-rel fail ())
(declare-rel inv2 (Int Int Int Int))
(declare-rel inv (Int Int))
(declare-var A Int)
(declare-var B Int)
(declare-var C Int)
(declare-var D Int)
(declare-var E Int)
(declare-var F Int)
(declare-var G Int)
(declare-var H Int)
(rule (=> (and (= A 2500) (= C 15000)) (inv A C)))
(rule (=> (and (inv A C) (= H 0) (= G 0) (= D (* 3 A)) (= C (* 6 A)) (= (* 5 A) B))
    (inv2 H G D B)))
(rule (let ((a!1 (= F
              (ite (>= H D)
                   (ite (>= H B) (- G 2) (+ G 1))
                   (ite (>= H A) (+ G 1) (- G 2))))))
  (=> (and (inv A C) (inv2 H G D B) (= E (+ H 1)) a!1) (inv2 E F D B))))
(rule (=> (and (inv A C) (inv2 H G D B) (= H C) (not (= G 0))) fail))
(query fail)


