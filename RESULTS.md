# Results (28 Oct 2026)

**Scope.**  4 of the 418 Comparator challenges (4 of 545 challenge theorems) were built and refereed:
`PeriodicGroup`, `OddKaplansky`, `CharacterVarietiesAllSeamsSupport`, `CartierChartCompactnessSupport`.  They were
chosen as the smallest import closures that reach an `opaque` constant (3) and the two challenges whose statement file
imports OpenAI's own library (2;  CharacterVarieties is both).  Nothing below is a statement about the other 414.
Every claim was written in `PREREG.md` before its measurement;  `PREREG.md` lists its one amendment (K4) and one
editorial revision, with dates and reasons.

Tools:  the referee and census of Discipline-Architecture-2 (`discipline/lean/`), at the commit printed in each
output.  Comparator was not run (it needs Linux's `landrun`);  where its checks are compared, its two documented checks
are reimplemented and labelled as such (`benchmark/Compare.lean`).

## The pre-registered claims

| claim | result | evidence |
|---|---|---|
| K1:  only the three permitted axioms | **holds** on all 4 headline theorems | `results/*/referee*.out`, L0 |
| K2:  no stand-in (L1 FAIL) | **holds** on all 4 | L1 |
| K3:  opaque-reaching theorems lie in the 13 directories found statically | **holds** on all 4 | L1, `scans/opaque.tsv` |
| K4 (amended):  no challenge statement reaches an `opaque` | **fails** on CharacterVarieties (`cutGeneratorWitness`) | `results/K4-interim.md` |
| K5:  every accepted user theorem is classed | **holds** (the only unclassed ones are 5 generated `congr_simp`) | `results/*/census*` |
| M1:  library-importing challenges carry solution-side definitions in their statements | **holds**:  18 (Cartier), 599 (CharacterVarieties) | `results/M1-M2.md` |
| M2:  Mathlib-only challenges carry none | **holds** on both built (PeriodicGroup, OddKaplansky) | `results/M1-M2.md` |
| M3:  local definitions per statement, beside the paper's claim | recorded;  **a reading** | `results/M3-readings.md` |
| M4:  planted faults:  Comparator's checks pass all 4, the referee flags all 4 | **holds** | `results/M4-benchmark.md` |

## What the results show

- **Where they agree.**  Every proof built here is kernel-checked with only the three axioms.  Nothing failed
  outright.
- **Where the statement is fixed by Mathlib alone,** it is short and says what the headline problem asks
  (PeriodicGroup, OddKaplansky;  M2, M3).
- **Where the statement imports the solution's library,** its meaning is largely defined by the code under test (M1),
  in one case partly behind a hidden value (K4).  These two are supporting lemmas, and the papers' headline results
  are not what was checked;  OpenAI's scope notes say so in words, and a passing Comparator run does not show it.
- **On faults planted on purpose,** Comparator's two checks pass all four;  the referee flags each with the check
  built for it (M4).
- **One discrepancy for a reader:**  OddKaplansky's family title and first scope line (torsion-free, characteristic
  two) against its formal statement (a torsion element, characteristic `p`).

## Limits

- 4 of 418 challenges is a small, chosen sample, not a random one.  The two library-importing challenges are all of
  their kind;  the Mathlib-only results (M2) cover 2 of 416.
- Comparator's checks are reimplemented, not run.
- M3 and the OddKaplansky discrepancy are readings;  whether a definition means what a paper means is not decided by
  any program here.
- Nothing here judges whether the mathematics is new or correct beyond what the kernel checks.
