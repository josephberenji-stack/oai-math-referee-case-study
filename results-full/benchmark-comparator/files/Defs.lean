import Mathlib.NumberTheory.LSeries.RiemannZeta

/-! Shared definitions for the planted-fault benchmark. -/
namespace Bench
/-- (a) a value hidden behind `opaque`. -/
opaque hiddenK : ℕ := 7
/-- (b) a hypothesis package that nothing on file builds. -/
structure Oracle where
  /-- the package carries the target. -/
  carries : RiemannHypothesis
/-- (d) a goal that is true by unfolding. -/
def Goal : Prop := ∀ n : ℕ, n = n
end Bench
