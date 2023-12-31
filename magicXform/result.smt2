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
(declare-var J Int)
(declare-var K Int)
(rule (=> (and (= I 0) (= D B) (= K A) (= F C) (= 3000 C) (= 1000 B) (= 2000 A))
    (inv2 I D K F C B A)))
(rule (let ((a!1 (and (inv2 I D K F C B A)
                (= E (+ 1 I))
                (= J (ite (>= I B) (+ D 1) D))
                (= G (ite (>= D A) (+ K 1) K))
                (= H (ite (>= K C) (+ F 1) F)))))
  (=> a!1 (inv2 E J G H C B A))))
(rule (=> (and (inv2 I D K F C B A) (>= K C) (not (= I F))) fail))
(query fail)

