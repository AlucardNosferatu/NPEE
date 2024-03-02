Require Import Reals.
Local Open Scope R_scope.

Theorem jiaohuanlv : forall a b: R,
 a+b=b+a.
Proof. Admitted.

Theorem jiehelv : forall a b c: R,
 (a+b)+c=a+(b+c).
Proof. Admitted.

Theorem jiaohuanlv2 : forall x y z:R,
 x+y+z=z+y+x.
Proof.
 intros.
 rewrite jiehelv.
 rewrite (jiaohuanlv x (y+z)).
 rewrite (jiaohuanlv y z).
 reflexivity.
Qed.

 
Theorem jiaohuanlv3 : forall x y z:R,
 x+y+z=z+y+x.
Proof.
 intros.
 rewrite jiaohuanlv.
 assert(H:x+y=y+x).
 {
  rewrite jiaohuanlv.
  reflexivity.
 }
 rewrite H.
 rewrite jiehelv.
 reflexivity.
