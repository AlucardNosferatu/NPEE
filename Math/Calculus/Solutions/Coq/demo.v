Theorem plus_id_example : forall n m: nat,
 n=m->
 n+n=m+m.

Proof.
 intros n m.
 intros A.
 rewrite -> A.
 reflexivity. Qed.