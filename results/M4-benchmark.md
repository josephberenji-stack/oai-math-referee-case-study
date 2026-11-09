# M4:  the planted-fault benchmark (28 Oct 2026)

Files:  `benchmark/Defs.lean`, `Challenge.lean` (statements, `sorry`), `Solution.lean` (proofs), `Compare.lean`
(Comparator's two documented checks, **reimplemented**:  the solution theorem's type equals the challenge theorem's
type, and its axioms are among `propext`, `Quot.sound`, `Classical.choice`;  Comparator itself needs Linux's `landrun`
and was not run).  Lean 4.33.1, Mathlib only.  Referee:  Discipline-Architecture-2 at 474014d, registry
`referee/registry-bench.tsv` (`open RiemannHypothesis`).  Raw output:  `results/benchmark-referee.out`.

| theorem | planted fault | Comparator's checks | referee |
|---|---|---|---|
| `fa` | the statement's meaning runs through an `opaque` value | PASS | L1u REVIEW (statement-level `hiddenK`) |
| `fb` | the target under a hypothesis package nothing builds | PASS | L2 FAIL (UNBUILT), class C |
| `fc` | an `↔` with the registered target | PASS | R2 FAIL (restatement), class B |
| `fd` | true by unfolding a definition | PASS | R1 FAIL (structural), class DEF |
| `fe` | intended as clean | PASS | R1 FAIL, class DEF |

**M4 holds:**  Comparator's two checks pass all four planted faults;  the referee flags all four, each by the check
built for it.

**The control row is mine to correct, not the referee's.**  `fe : 0 < n → 1 ≤ n` was meant as a clean theorem, but on
`ℕ` the statement `1 ≤ n` is `0 < n` by definition, so it does hold by unfolding alone and DEF is the right class.  A
clean control should reach a real library theorem (as `fa`'s `le_refl` does).

Both checks agree that every proof is kernel-checked with the three axioms.  The difference is what each reports
about what was proved.
