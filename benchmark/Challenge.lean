import Bench.Defs
/-! The challenge:  statements only. -/
namespace Bench
theorem fa : ∃ n : ℕ, hiddenK ≤ n := sorry
theorem fb (O : Oracle) : RiemannHypothesis := sorry
theorem fc : RiemannHypothesis ↔ (RiemannHypothesis ∧ True) := sorry
theorem fd : Goal ↔ ∀ n : ℕ, n = n := sorry
theorem fe (n : ℕ) (h : 0 < n) : 1 ≤ n := sorry
end Bench
