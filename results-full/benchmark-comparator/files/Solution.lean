import Bench.Defs
/-!
# Planted-fault benchmark:  the solution

Four planted faults and one clean theorem.

## Main results

* `fa`: a statement whose meaning runs through the hidden value `hiddenK`.
* `fb`: the target under a hypothesis package nothing builds.
* `fc`: an equivalence with the registered target.
* `fd`: holds by unfolding a definition.
* `fe`: clean.
-/
namespace Bench
open Bench
/-- (a) the statement reaches a hidden value. -/
theorem fa : ∃ n : ℕ, hiddenK ≤ n := ⟨hiddenK, le_refl _⟩
/-- (b) the target, given a package that carries it. -/
theorem fb (O : Oracle) : RiemannHypothesis := O.carries
/-- (c) a restatement of the target. -/
theorem fc : RiemannHypothesis ↔ (RiemannHypothesis ∧ True) := ⟨fun h => ⟨h, trivial⟩, fun h => h.1⟩
/-- (d) true by unfolding `Goal`. -/
theorem fd : Goal ↔ ∀ n : ℕ, n = n := Iff.rfl
/-- (e) a clean theorem. -/
theorem fe (n : ℕ) (h : 0 < n) : 1 ≤ n := h
end Bench
