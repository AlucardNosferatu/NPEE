import Mathlib.LinearAlgebra.Matrix.Adjugate
import Mathlib.Data.Real.Sqrt

namespace Matrix

  def m2 : Type := ℕ
  def n2 : Type := ℕ
  def a2 : Type := ℝ

  variable
  [Fintype n2]
  [DecidableEq n2]
  [CommRing a2]

  variable (A : Matrix n2 n2 a2) (B : Matrix n2 n2 a2)

  def matrix1 : Matrix (Fin 2) (Fin 2) ℝ :=
  ![![1,2],![3,4]]
  def matrix2 : Matrix (Fin 2) (Fin 2) ℝ :=
  ![![5,6],![7,8]]
  def matrix_unit : Matrix (Fin 2) (Fin 2) ℝ :=
  ![![1,0],![0,1]]
  def matrix1_adj : Matrix (Fin 2) (Fin 2) ℝ := adjugate matrix1
  def matrix1_det := matrix1.det
  -- matrix1_det • matrix_unit = matrix1_adj * matrix1
  def my_set := (Finset.univ : (Finset (Fin 2)))
  def sum_of_numbers : ℕ :=
  Finset.sum (Finset.range 11) (fun x => x)
  def sum_of_numbers2 : ℕ :=
  Finset.sum my_set (fun x => x)

  def matrixb : Fin 2 → ℝ := ![5,6]
  def cramer001 := cramer matrix1 matrixb
  -- #eval cramer001
  def solution := (matrix1_det) • (cramer matrix1 matrixb)
  #eval solution

end Matrix
