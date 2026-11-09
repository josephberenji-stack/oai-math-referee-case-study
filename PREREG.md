# Pre-registration (written 28 Oct 2026, before any compiled run)

Source: github.com/openai/math at `7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a`, `lean/` (toolchain `leanprover/lean4:v4.34.1`).
Referee: Discipline-Architecture `discipline/lean/`, at the commit recorded in each run's output.
Budget: one formulation per claim. A claim that fails is reported as failed, not reworded.

## What is already measured (static, `scans/summary.txt`; a count of text, not of compiled constants)

| quantity | value |
|---|---|
| `.lean` files under `lean/OAI` | 162,417 |
| Comparator configs / challenge theorems | 418 / 545 |
| configs whose permitted axioms are not exactly `propext, Quot.sound, Classical.choice` | 0 |
| challenge files with no local definition | 12 |
| files with `sorry`, `admit`, `axiom`, `native_decide`, `implemented_by`, `@[extern]`, `unsafe` in code | 0 each |
| files using `decide +kernel` | 5,848 |
| `opaque` declarations | 1,542 (1,506 in `MathematicalPhysics/ContinuumCoulomb`; the rest in 12 other directories) |
| of those, with no value | 0 |
| of those whose value is a `⟨_, rfl⟩` pair | 25 (1,159 other terms, 358 tactic proofs) |

Correction on record: an earlier scan (27 Oct) reported 42 `opaque` constants "wrapping proved values". That scan
matched only declarations beginning `opaque`, and missed the 1,492 written `noncomputable opaque`. The figure above
replaces it.

## Claims for the compiled runs

Each claim names its check, what would kill it, and how it is counted. The unit is a challenge theorem (545), read
through its solution module.

- **K1 (L0).** All 545 challenge theorems depend only on the three permitted axioms.
  Kill: one theorem with any other axiom.
- **K2 (L1 FAIL).** No challenge theorem reaches an `opaque` with no value, or an `unsafe`, `partial`,
  `@[implemented_by]` or `@[extern]` constant. Kill: one L1 FAIL.
- **K3 (L1 REVIEW, scope).** Every challenge theorem that reaches an `opaque` with a value has its solution under one of the
  13 directories listed in `scans/opaque.tsv`. Kill: one such theorem in any other family.
- **K4 (L1u), amended 28 Oct 13:15 UTC, before any L1u run.** Every `opaque` reached by a challenge theorem is reached
  only from its proof, never from the challenge statement (outcome `proof-only` on every row). Kill: one
  `statement:*` row for a challenge theorem. Control: a planted theorem whose statement mentions an `opaque` must
  come out `statement:*`.
  *Why amended:* the first K4 ("never `hidden-proof`") could not fail. Making an `opaque` transparent only adds
  definitional equalities, so no proof can depend on the hiding. The L1u design is corrected to match
  (Discipline-Architecture-2, `discipline/lean/L1U-DESIGN.md`).
- **K5 (census).** Every accepted user theorem of the solution modules in scope gets a CLASS row.
  Kill: one row in `accepted-not-classed.tsv` that is not a generated name.

## Recorded, not predicted

The counts of class C (an unbuilt hypothesis, L2), DEF (R1), B (R2/R6), RED (L3) and R7 REVIEW over the 545
theorems, and for each one, the hypothesis or the lemma named. No prediction is made for these. They are the
substance of the case study and are reported as found, per family.

## Not decided by any run here

Whether a challenge statement says what its paper claims. Whether a custom definition means what its name says.
Novelty. These stay with a person, as REVIEW.

## Order of work

1. Approval to build the upstream library (its lakefile clones and patches dependencies).
2. Build only the solution modules of the challenges in scope, one at a time, with a memory cap.
3. Run the referee (`--modules`), then the census, then L1u once it is built, then report each claim as stated.

## Note on the ContinuumCoulomb opaques (static reading, 28 Oct 2026, before any compiled run)

The 1,506 `opaque` declarations under `MathematicalPhysics/ContinuumCoulomb` (family 275, challenge
`ContinuumCoulombHardness`, theorems `unit_coulomb_qmaHard` and `binary_coulomb_qmaHard`) are written
`noncomputable opaque NAME : Procedure enc enc f := ...`. A `Procedure` (`OAI/Computability/QuantumFactoring/
BitStackProcedures.lean:43`) bundles a program, a polynomial time bound, and a proof that the program computes `f` within
that bound. The type states the whole specification. The reading to be tested by K4 is that the hiding is cosmetic
(stopping the kernel from unfolding large programs): the challenge statements never reach these constants.
This family is the first build target.

## Addendum, 28 Oct 2026 13:40 UTC:  does the meaning slide while the proof holds?

The question:  where a proof is kernel-checked, does the *meaning* of what was proved move away from the paper's
claim while the proof itself holds?  Stated here as a hypothesis that can fail, with a claim (M2) whose holding counts
in favour of the checked work.  Written before any of the measurements below were made, except
where a row says it is already on file.

**Definitions.**  A challenge's *statement closure* is every constant its headline statement reaches through the
types and values of the definitions it uses, stopping at `opaque` values (the referee's `stmtClosure`).  Each constant
in it is *library* (Lean core, Mathlib and its packages), *challenge-local* (declared in the challenge file), or
*solution-side* (declared in OpenAI's `OAI` library).  Comparator fixes a statement against its challenge file;  it
does not ask which of these three the meaning comes from.

**Static fact on file (scans, 28 Oct):**  416 of the 418 challenge files import only Mathlib;  2 import `OAI`
(`CharacterVarietiesAllSeamsSupport`, `CartierChartCompactnessSupport`).

**Claims.**
- **M1.**  Every challenge whose file imports `OAI` has at least one solution-side constant in its statement closure.
  Kill:  one such challenge with none.  (CharacterVarieties is already known to satisfy it, through
  `cutGeneratorWitness`;  the claim is decided by `CartierChartCompactnessSupport`.)
- **M2.**  No challenge whose file imports only Mathlib has a solution-side constant in its statement closure:
  Comparator's design holds there.  Kill:  one such challenge with one.  *(A hold here is evidence for their method,
  and is reported as such.)*
- **M3.**  For each challenge in scope, the count of challenge-local definitions in its statement closure is recorded,
  with the paper's headline written independently beside it.  No prediction:  this is the size of the gap Comparator
  does not measure, reported per family.
- **M4 (planted faults).**  In a separate copy, four faults are planted into a small challenge:  (a) an `opaque` value
  inside the statement;  (b) an unbuilt hypothesis structure;  (c) a statement that is an `↔` with a registered
  target;  (d) a theorem that holds by unfolding definitions only.  Prediction:  Comparator's two checks (statement
  match, axiom whitelist) pass all four;  the referee flags all four.  Kill:  the referee misses one, or Comparator's
  checks reject one.  If Comparator itself cannot run on this machine (it needs Linux's `landrun`), its two documented
  checks are reimplemented and the report says so.

**Not decided by any run here:**  whether a challenge-local definition means what the paper means.  A slide is shown
only where the statement's meaning demonstrably comes from solution-side or hidden constants;  everything else is
reported as a measured gap, not as a slide.

## Revisions

- 28 Oct 2026, ~14:50 UTC, after M1–M4 were run:  the addendum's opening sentence was reworded from a quotation of
  the project owner to a neutral statement of the question.  No claim, kill condition or control was changed.
- 28 Oct 2026, ~15:25 UTC, before the full run:  `scripts/run_all.py` gives each copy its own temporary file and
  appends each challenge's rows to `summary.tsv` (under a file lock) as soon as that challenge is done, so several
  copies can run at once on disjoint `--only=` lists and an interrupted run keeps the rows it produced.  No computed
  value, claim, kill condition or control was changed.  The machine run is `scripts/oai-vm.sh` (`CLOUD-PLAN.md` § 10).

## Full run (all 418 challenges), written 28 Oct 2026 ~15:15 UTC, before it is run

To be run on a Linux cloud machine by `CLOUD-PLAN.md`;  `scripts/run_all.py` was tested on PeriodicGroup, OddKaplansky
and CartierChartCompactnessSupport (which reproduce the counts in `results/`) before this section was written.  The
unit is a challenge theorem (545), through its solution module.  Kernel acceptance of every configuration is cited from
the community's check (Lean Zulip, "Checking all of OpenAI's Lean library: build cost, nanoda"), not claimed here.

- **F1 (L0).**  Every challenge theorem depends only on the three permitted axioms.  Kill:  one with another axiom.
- **F2 (L1).**  No challenge theorem reaches a stand-in (L1 FAIL).  Kill:  one L1 FAIL.
- **F3 (L1u).**  Statement-level hidden values occur only in challenges whose file imports `OAI`:  no challenge
  theorem of a Mathlib-only challenge has L1u REVIEW.  Kill:  one.
- **F4 (M2 everywhere).**  No challenge theorem of a Mathlib-only challenge has a solution-side definition in its
  statement (generated instances of challenge-local types counted as local, `run_all.is_local`).  Kill:  one.
- **F5 (census).**  No accepted theorem a person named is left unclassed in any solution module.  Kill:  one census row
  whose shape is `other` or `eq_ (a person's name)`.
- **F6 (Comparator on the benchmark).**  Real Comparator accepts all four planted faults `fa`–`fd`.  Kill:  it rejects
  one (that would mean its checks are stronger than the reimplementation, and M4 is withdrawn for that fault).
- **Recorded, not predicted.**  Per challenge theorem:  L1, L1u, L2 and class;  the number of challenge-local and
  solution-side definitions in its statement;  the distribution of challenge-local definition counts over all 418;
  every L2 FAIL or REVIEW with its hypothesis.

## Library pass (every compiled `OAI` module), written 28 Oct 2026 ~18:10 UTC, before it is run

A second scope, separate from the 545 challenge theorems above.  Its unit is a module of openai/math's `OAI` library
in **the import closure of the 418 configurations**:  every `OAI` module imported, directly or not, by a configuration's
solution module or by a file in `ComparatorChallenges/` (which includes the Hodge folder's `Solution.lean`), and every
declaration in it.  This is the denominator of G1–G4, not the whole library:  the number of modules in the closure is
recorded from the build, beside the number of `OAI` modules in the library, and the report states both.  "Every
compiled `OAI` module" below means every module of this closure.  It runs only after the full run's results are
committed, on the same built library.

**What "inconsistency" means here.**  Only what the referee and census flag:  an axiom beyond `propext`,
`Quot.sound`, `Classical.choice`;  a stand-in (`sorryAx` or a project placeholder);  a hidden value
(an `opaque` or `implemented_by` value) in a statement (L1u REVIEW);  a hypothesis that nothing in the library
builds or that carries a proposition (L2 FAIL / REVIEW);  a statement that holds only by unfolding a definition
(class DEF);  a theorem a person named that nothing classes (census).  It does not mean a logical contradiction.
Kernel acceptance of every configuration is cited from the community's check;  nothing in this pass looks for a
proof of `False`, and no result here is reported as one.

- **G1 (L0).**  Every theorem in every compiled `OAI` module depends only on the three permitted axioms.
  Kill:  one theorem with another axiom.
- **G2 (L1).**  No theorem in a compiled `OAI` module reaches a stand-in.  Kill:  one L1 FAIL.
- **G3 (opaques).**  Every L1u REVIEW (a hidden value in a statement) is in a module under
  `OAI.MathematicalPhysics.ContinuumCoulomb` or under the `OAI` modules that the two `OAI`-importing challenges
  (`CartierChartCompactnessSupport`, `CharacterVarietiesAllSeamsSupport`) reach.  Kill:  one L1u REVIEW elsewhere.
  (The static scan found 1,542 `opaque` declarations, 1,506 of them in ContinuumCoulomb;  this predicts that the
  rest do not reach a statement outside those two places.)
- **G4 (census).**  No accepted theorem a person named is left unclassed in any compiled `OAI` module.
  Kill:  one census row whose shape is `other` or `eq_ (a person's name)`.
- **Recorded, not predicted.**  Per module:  the number of theorems, and of each class (A?, DEF, C, B, RED, D,
  C-vacuous);  every L2 FAIL or REVIEW with its hypothesis;  every L1u REVIEW with the hidden value it reaches;  the
  census's unread count.  Totals over the library, and the modules ranked by DEF share.

**How it runs.**  The same referee and census (Discipline-Architecture-2 at the commit in `RUN-INFO.md`), with
`--modules=` set to every `OAI.*` module that has a compiled `.olean` after the full run's build, one process per
module group, memory-capped as in the full run.  Results go to `results-library/` and `RESULTS-LIBRARY.md`, under
the same rules as the full run (report held / failed / not evaluated;  a failure is a result;  nothing dropped from the
denominator).

**Observed before this was written (recorded, not a claim).**  The full run's `chalbuild` stage builds more than the
challenge files' own imports:  `ComparatorChallenges/HodgeConjectureCMAbelianVarieties/` keeps a `Solution.lean`
(importing `OAI.AlgebraicGeometry.HodgeConjecture.MainSubmission`) inside the challenges folder, so building that
folder builds the Hodge closure.  The two challenge files that import `OAI` directly are still only
`CartierChartCompactnessSupport` and `CharacterVarietiesAllSeamsSupport`;  "416 challenges import only Mathlib"
holds for the challenge files themselves.

- 28 Oct 2026, ~18:12 UTC, before the library pass runs:  its denominator stated as the import closure of the 418
  configurations (module count from the build, beside the library's total), not "every compiled module".  No claim or
  kill condition changed.

## The Hodge configuration (a 419th challenge outside the 418), written 28 Oct 2026 ~21:00 UTC, before it is run

`ComparatorChallenges/HodgeConjectureCMAbelianVarieties/` holds its own configuration, `main.json` (one theorem,
`HodgeCM.hodge_conjecture_for_cm_abelian_varieties`;  no definition holes;  the three standard axioms), its own
`Challenge.lean`, `CM.lean` and `Solution.lean`.  Because the configuration is not at the top of `ComparatorChallenges/`,
the 418 above do not include it.  Its solution imports `OAI.AlgebraicGeometry.HodgeConjecture.MainSubmission`, whose
import closure is 33,169 `OAI` modules (static count from the source's import lines), none of them used by any of the
418 solution modules.  The challenge statement's meaning rests on `CM.lean` and on the library `HodgeConjecture`:
257 helper files kept inside the challenge folder ("preserved challenge sources under their original HodgeConjecture
module names", openai/math `lean/lakefile.lean:112`;  marked as Formal Conjectures sources, modified), which the lakefile
enumerates through its own library facet (`lakefile.lean:118-136`).  It is checked after the full run, on the same built
disk, with the referee, the census, the statement-origin pass and real Comparator.

- **H1 (L0).**  The theorem depends only on the three permitted axioms.  Kill:  another axiom.
- **H2 (L1).**  It reaches no stand-in.  Kill:  an L1 FAIL.
- **H3 (Comparator).**  Real Comparator accepts `main.json`.  Kill:  it rejects (recorded with its message).
- **H4 (origins).**  No definition the statement reaches is declared in an `OAI` module:  its meaning comes only from
  Mathlib, `CM.lean` and the `HodgeConjecture` helpers.  Kill:  one `OAI`-declared definition in the statement.
- **H5 (census).**  No accepted theorem a person named in the solution's closure is left unclassed.  Kill:  one census
  row whose shape is `other` or `eq_ (a person's name)`.  (Run on the closure's modules as the library pass is.)
- **Recorded, not predicted.**  L1u and L2 on the theorem (hypotheses `IsIntegral`, `Smooth`, `IsProjective`,
  `GrpObj`, `HasComplexMultiplication`);  the number of `HodgeConjecture` helper and `CM.lean` definitions the statement
  reaches;  the classes over the 33,169-module closure;  the lakefile's custom facet as a dependency of the challenge
  (miss mode G).  Reported separately from the 418, beside them, never folded into their totals.
- 28 Oct 2026, ~21:10 UTC, before the Hodge entry runs:  `scripts/run_all.py` takes `--config=PATH.json` (a configuration
  outside the top of `ComparatorChallenges/`, e.g. Hodge's `main.json`) and reads each challenge file from its module name
  (so a subfolder's `Challenge.lean` is found);  `--helpers=HodgeConjecture` makes the statement-origin pass
  (`scripts/StmtOrigins.lean.tmpl`) follow those modules' definitions and report them as a third origin,
  "challenge-folder helper" (`HDEF`, column `challenge_folder_helper_defs`), never as solution-side.  H4 is evaluated on
  `ODEF` (definitions declared in `OAI` modules) only.  The run_all.py here starts from the full run's version (several
  copies at once, rows appended under a lock) so that merging `main` into `full-run` adds only these changes.  No claim or
  kill condition changed.  The Hodge pass:  `python3 -I scripts/run_all.py sources/openai-math/lean ../da2/discipline/lean
  results-hodge --config=ComparatorChallenges/HodgeConjectureCMAbelianVarieties/main.json --helpers=HodgeConjecture`, then
  Comparator on the same `main.json`;  H4's expected outcome already follows from the helper files' import lines (no `OAI`
  import), so its run is a check of that source scan from the compiled constants, not a separate finding.
- 28 Oct 2026, ~21:30 UTC, before the Hodge entry runs:  wording corrected.  The 257 helper files carry Formal
  Conjectures copyright lines, but only `Challenge.lean` says "This file has been modified";  "marked as Formal
  Conjectures sources, modified" above should read "with Formal Conjectures copyright lines".  A static comparison with
  their upstream (Paul Lezeau's HodgeConjecture) is recorded in `results/HODGE-STATIC.md`.  No claim changed.

## The new referee checks on the library pass and the Hodge pass, written 28 Oct 2026 ~22:10 UTC, before either runs

Discipline-Architecture-2 gained five checks for proofs built from supplied inputs (`discipline/lean/INPUTS-DESIGN.md`):
R1i (an input supplied by a theorem that holds by unfolding alone), DUP (two definitions with one body under two names,
crossed without a proved equivalence), SHADOW (a project copy of a library declaration), INST (a module that removes an
instance or adds a local or scoped one), VEND (a project module under a `Mathlib` folder). Self-test 61/61, every check
needed. **The library pass and the Hodge pass run with Discipline-Architecture-2 at commit
`e0854d5cb6bdf52e45506659f4fa1633d0735256`** (not the commit the full run used), and record it in their results.

On the Hodge configuration (`main.json`; theorem and closure as in "The Hodge configuration" above):
- **N1 (R1i).**  Every input the Hodge proof supplies carries content:  R1i on the Hodge theorem is PASS.  Kill:  REVIEW
  (an `Established` theorem that holds by unfolding alone).
- **N2 (SHADOW).**  SHADOW on the Hodge theorem is REVIEW:  its closure reaches a project copy of a library declaration
  (`MainSubmission.lean:11-13` describes an older module with the same names and types).  Kill:  PASS.
- **N3 (VEND).**  Every module of the closure stored under `HodgeConjecture/Mathlib/` is VEND REVIEW.  Kill:  one PASS.
- **N4 (INST).**  `OAI.AlgebraicGeometry.ComplexMultiplication.Reference.GeometricAlgebraicity` is INST REVIEW (it
  removes an instance).  Kill:  PASS.
- **Recorded, not predicted.**  DUP on the Hodge theorem, with its pairs.  DUP sees twins inside one environment only;
  the challenge-versus-solution names (`HodgeCM.*` against `OAI.*`, `results/HODGE-STATIC.md`) live in two environments
  and are Comparator's question (H3), not DUP's.

On the library pass (the closure of the 418 configurations):  recorded, not predicted:  per check, the number of
theorems (R1i, DUP, SHADOW) or modules (INST, VEND) with REVIEW, and every R1i and DUP row in full.  A static count made
before this was written found `attribute [-instance]` or `attribute [local instance]` in 12,503 `OAI` files (whole
library);  INST's count over the closure is compared with the same static count over the closure as a check of the
instrument.

## A referee fault found before the library and Hodge passes, written 28 Oct 2026 ~23:45 UTC, before either runs

Running the referee over our own build, a Lean process that ran out of memory printed no error line, and the referee
then reported no rows for that module, which reads as a pass. Discipline-Architecture-2 commit
`5a4b81f` makes such a run `REFEREE BUILD FAIL` (exit code and last line); self-test 61/61. The passes stay pinned to
`e0854d5` as registered above. Analysis rule, fixed now: a module or configuration whose referee output has no
`REFEREE` row for a theorem it holds is counted as **BUILD FAIL (silent)**, never as PASS, and listed. A run with
`5a4b81f` instead is reported as such, with this entry as the reason. No claim or kill condition changed.

## The behaviour test on the library (claims B0–B5), written 30 Oct 2026 ~22:00 UTC, before it is run

A separate test with its own claims, outputs and report.  It changes no verdict of K, M, G or H, and none of them
changes it.  It asks of each definition it reaches:  does this object behave like an object Mathlib already has, and
like the one its name claims?  Method:  the behaviour step of Discipline-Architecture-2 `discipline/lean/BEHAVIOUR-DESIGN.md`
(shape by carrier sequence, probes per carrier class built by each side's own constructors, the candidate's own laws
checked with the definition in its place;  a candidate at `S ≥ 0.8`), unchanged.

**Unit.**  One definition (`def`, `structure`, `class`):  challenge-local, in a statement closure of the 418
configurations (M3's rows), or solution-side, in their import closure (the library pass's denominator).
Budget:  one formulation per claim.  A claim that fails is reported as failed, not reworded.

**Order.**  (1) B0 holds;  (2) the full run's re-runs, solution rebuild, solution-side referee and the Hodge pass are
done;  (3) the library dump (MDECL lines) is redone against this library's own toolchain (v4.34.1) and Mathlib pin, and
its md5 recorded before scoring;  (4) the run:  one Lean process at a time, memory-capped as in the full run.

- **B0 (gate).**  The behaviour step, at the Discipline-Architecture-2 commit named in `RUN-INFO.md`, passes all seven
  controls of `BEHAVIOUR-DESIGN.md` on its own control set.  Kill:  one failed control.  If B0 fails, B1–B5 are not run.
- **B1 (planted, on this library's pin).**  A separate copy holds three planted challenge-local definitions:
  (a) `choose'`, a renamed copy of `Nat.choose`;  (b) `choose`, off by one at k = 0;  (c) a definition on a new
  inductive.  Prediction:  `Nat.choose` is in (a)'s top 10 with `S ≥ 0.8`;  (b) scores below 0.8 on `Nat.choose`;
  (c) gets 0 candidates.  Kill:  any one of the three.  If B1 fails, B2–B5 are reported as not evaluated.
- **B2 (named objects).**  Every challenge-local definition whose name, or its last component, is the name of a Mathlib
  declaration of the same shape scores `S ≥ 0.5` on that declaration's laws.  Kill:  one such definition below 0.5 that
  a person's reading confirms behaves differently.  *(A hold here counts in favour of their method, and is reported so.)*
- **B3 (copies).**  Recorded, not predicted:  the solution-side definitions with `S = 1` on at least 10 laws of one
  Mathlib object (behavioural copies of an object Mathlib has), per family, with the object named.
- **B4 (coverage).**  Recorded, not predicted:  per family, the share of definitions with at least one candidate and the
  share with none.  Analytic shapes (ℝ, ℂ) are reported apart:  their laws are checked by a fixed proof script, which can
  only miss.
- **B5 (cross-family control, on this library).**  Each definition scored against the expected object of a row of
  another shape class, 1,000 pairings, seed 20261030.  Kill:  5 % or more of pairings reach `S ≥ 0.8`.  If B5 fails,
  B2–B4 are reported with that failure beside them.

**Outputs.**  `results-behaviour/` (per-group `behaviour.tsv`, controls JSON, dumps with MD5) and
`RESULTS-BEHAVIOUR.md`:  every claim held, failed or not evaluated;  nothing dropped from the denominator.

**Not decided by any run here.**  Whether a definition means what the paper means.  A low score is a lead for a person,
not a slide;  a slide is shown only where a person's written reading confirms it.  A definition with no candidate is
reported as "no candidate within the step's reach", not as new mathematics, until a person has read it.

## The Hodge closure in full, with the expanded referee, written 1 Nov 2026 ~05:45 UTC, before it is run

The request (1 Nov 2026, 05:10 and 05:23 UTC) was to run the fully expanded referee over the Hodge configuration and its
standalone library in full, on the larger machine.  Read as:  the Hodge configuration ("The Hodge
configuration" above, `main.json`) and **every module of its import closure** (33,169 `OAI` modules, static count, plus
the 257 helper files), built and refereed.  The H and N claims above stand unchanged and run here.  This section adds
the closure claims and the checks built since 28 Oct.  The 418 and their library pass are not part of this run.

**The referee.**  Discipline-Architecture-2 at the commit printed in `RUN-INFO.md`:  `main` after merging the branch
`referee-expanded-2026-11-01` (the behaviour, decode, drift, unfold and R1k lanes;  the control-name fix, PR #4;  the
IFF check).  Its self-test (all expectations) and mutation test (every check needed) are printed beside it.  Not the
commits the full run (a98736bc) or the earlier H registration (e0854d5) named:  that is the point of this run, and the
H and N rows are reported against the commit used.  BUILD FAIL rule as in "A referee fault found…":  a module with no
`REFEREE` row for a theorem it holds is **BUILD FAIL (silent)**, listed, never counted as PASS.

**The closure (HC), per module of the closure.**
- **HC1 (L0).**  Every theorem depends only on the three permitted axioms.  Kill:  one theorem with another axiom.
- **HC2 (L1).**  No theorem reaches a stand-in.  Kill:  one L1 FAIL.
- **HC3 (opaques).**  No L1u REVIEW in the closure outside modules under `OAI.MathematicalPhysics.ContinuumCoulomb`
  (the static scan places 1,506 of the library's 1,542 `opaque`s there;  whether the closure imports any of them is
  read from the build, not assumed).  Kill:  one L1u REVIEW elsewhere.
- **HC4 (census).**  No accepted theorem a person named is left unclassed.  Kill:  one census row whose shape is
  `other` or `eq_ (a person's name)`.
- **Recorded, not predicted.**  Per module and in total:  the classes (A?, DEF, C, B, RED, D, C-vacuous);  R1k
  (CONTENT, FIELD, HYP, IND, UNFOLD);  IFF (FAIL, PASS, REVIEW);  R1i, DUP, SHADOW, INST and VEND REVIEW counts;  every
  L2 FAIL or REVIEW with its hypothesis;  the theorems whose names start with `control` (skipped by the full run's
  referee, checked now), listed;  every BUILD FAIL.
- **What changed since the full run, measured.**  On the Hodge theorem and on every closure module that the 418's
  solution modules also reach (if any):  each check's row under this referee beside the row under a98736bc, where one
  exists.  None is predicted.

**Not run here.**  The behaviour step (B0–B5):  its gate B0 failed in run 1 (Discipline-Architecture-2 METHOD-LOG entry
17), and it waits for run 2.  The drift check:  not yet defined.

**Order.**  (1) the referee commit fixed and printed;  (2) build the Hodge configuration's solution module and the
helper library;  (3) H1–H5, N1–N4 on the theorem;  (4) the referee and census on every closure module, one process per
module group, memory-capped;  (5) results to `results-hodge/` and `RESULTS-HODGE.md`, every claim held, failed or not
evaluated, nothing dropped from the denominator.

- 6 Nov 2026:  two quoted chat messages in the 1 Nov section were replaced by a plain statement of the request.  No claim or
  kill condition changed.
- 7 Nov 2026:  the public copy leaves out `CLOUD-PLAN.md`, the run plan named in lines 117 and 121.  Its stages and settings
  are in `logs/*/RUN-INFO.md` and the scripts in `scripts/`.  No claim or kill condition changed.
