# M3:  the paper's claim beside what the Lean statement rests on (28 Oct 2026)

**This file is a reading, not a measurement.**  The counts and the lists are measured (`results/M1-M2.md`,
`results/origins-*.txt`, the challenge files).  The comparison in the last column is one reader's judgement and is
REVIEW by the method:  no program decides whether a definition means what a paper means.  The headline column quotes
OpenAI's own scope notes (`lean/docs/NNN.md`) in summary.

| family | paper's headline (their scope note) | what the Lean statement says | rests on | reading |
|---|---|---|---|---|
| PeriodicGroup (247) | an infinite finitely presented periodic group exists (negative answer to the finitely presented Burnside question) | `MainStatement ∧ BurnsideStatement`:  some group is infinite, `Group.IsFinitelyPresented` (Mathlib) and `Periodic` (every element has finite order), with a Steinberg-group witness | 9 challenge-local definitions (`Root`, `Generator`, `bracket`, `letter`, `SteinbergRel`, `Steinberg`, `Periodic`, `MainStatement`, `BurnsideStatement`), 0 solution-side | **matches.**  `Periodic` is the standard definition;  "finitely presented" is Mathlib's.  The scope note states plainly that the nil-algebra conclusions are left out. |
| OddKaplansky (197) | Kaplansky's direct-finiteness conjecture fails:  a group algebra over a finite field of characteristic two (scope note);  the family's title says "torsion-free" | `MainClaim`:  for the prime `p = minFac((M!)² + 1)`, `M = C(1200, 600)`, a field of size `p⁴` and characteristic `p`, a finitely generated group **with an element g ≠ 1 of finite order**, and `a b` with `ab = 1`, `ba ≠ 1` | 4 challenge-local (`sourceM`, `sourcePrime`, `cellular`, `MainClaim`), 0 solution-side | **matches the conjecture's negation for one (K, G),** which is the whole of Kaplansky's statement (all fields, all groups).  Two points for a person:  the formal field has characteristic `p` (odd), while the scope note's first line says characteristic two;  and the group has torsion, while the family's title says torsion-free.  Either the title and note describe a companion statement, or they disagree with the formal one.  The formal statement is what was checked. |
| Cartier (066) | bounded klt complements for Fano contractions | compactness of a set of `closedChartFieldRetraction` values over one chart | 18 solution-side definitions, 0 challenge-local | **a supporting lemma, not the headline,** and the scope note says so explicitly ("does not construct ... Bounded klt complements ... are also outside").  Its meaning sits in OpenAI's own library (M1). |
| CharacterVarieties (027) | potential integral density on curve character varieties | `D.ProducedMarkedSeamEquations ...`:  produced marked values satisfy every seam equation, for a given `Diagram` | 599 solution-side definitions, one `opaque` value in the statement (`cutGeneratorWitness`), 0 challenge-local | **a supporting compatibility result, not the headline,** and the scope note says so ("Existence of integral points and Zariski density are not established").  Its meaning sits in OpenAI's library and partly behind a hidden value. |

**What this shows.**
- Where a challenge imports only Mathlib (PeriodicGroup, OddKaplansky), the statement is short and readable, and in
  both cases it says what the headline problem asks.  Credit to their design.
- Where a challenge imports OpenAI's library (Cartier, CharacterVarieties), the Lean statement is a supporting lemma
  whose meaning is defined by the solution's own code, and the paper's headline is not what was checked.  Their scope
  notes disclose this in words;  Comparator's pass does not show it.  Here the meaning, not the proof, is what moves:
  from the paper's headline to a lemma stated in the solution's own terms.
- One discrepancy for a person to settle:  OddKaplansky's title and first scope line (torsion-free, characteristic two)
  against the formal statement (a torsion element, characteristic `p`).
