# Where the meaning could slide:  the hypothesis, and the ways Comparator can miss it

Written 28 Oct 2026, from Comparator's own README and source (github.com/leanprover/comparator at
`865edc14486c3388e9225daa971da8e157488c3e`, read only;  per its README it is now merged into Lean core as
`lake comparator` from v4.35.0) and from openai/math's 418 configurations.  Every count below is from the files;
nothing here was run.

## 1. What Comparator guarantees

For every theorem listed in a configuration's `theorem_names`, if Comparator succeeds (README, "Introduction";
`Comparator/Compare.lean`):

1. **Same statement.**  The solution's theorem has the same type as the challenge's, and *every constant reached from
   that statement* (types and values, transitively, `runForUsedConsts`) is identical, as a whole `ConstantInfo`,
   in the challenge and the solution environments.  This is a deep check:  a definition the statement uses cannot be
   changed by the solution, and an `opaque`'s value is compared too.
2. **Axioms.**  The solution's proof uses only the configuration's `permitted_axioms` (here always `propext`,
   `Quot.sound`, `Classical.choice`).
3. **Kernel.**  The solution environment replays in the Lean kernel (optionally also in external kernels).

It guarantees this **under its stated assumptions** (README):  (1) the transitive imports of the challenge file and the
lakefile are controlled by you or trustworthy;  (2) the solution was not compiled earlier in the same environment;
(3–4) the sandbox (`landrun`) works;  (5) the kernel is correct;  (6) not run as a privileged user.  And for
`definition_names` ("definition holes") it guarantees only name, type, universes and safety:  the README says such
challenges "**must** always be checked with an additional (potentially human) verifier".

## 2. The hypothesis

**Comparator closes the gap between the challenge statement and the proof.  What it leaves open is the gap between the
challenge statement and the claim in the paper.**  If meaning slides while every proof holds, it slides in one of the
places Comparator does not look:  in who defines the statement's objects, in what those objects mean, in what the
statement assumes, or in which claims were turned into challenges at all.

## 3. The miss modes, ranked by how directly they can move meaning

| # | miss mode | why Comparator cannot see it | where to search in openai/math | what finds it | so far |
|---|---|---|---|---|---|
| A | **The challenge imports the solution's own library.** Assumption (1) then rests on code written with the solution. | it checks that the definitions are *equal*, not who wrote them | the 2 configurations whose challenge file has `import OAI` | statement-origin pass (M1), L1u (K4) | both confirmed:  18 and 599 solution-side definitions in the statement;  one reaches a hidden value |
| B | **Definition holes.** The solution chooses the value of a definition the statement uses. | by design it checks only the hole's type | configurations with non-empty `definition_names`:  1 (`ElementaryPositivity`, hole `elementaryPositivityWitness`) | read the hole's type:  does it pin the meaning?  Here the type `PermutationWitness` itself contains the expansion, so the theorem restates a field of the witness;  the content is the witness's existence | 1 of 418;  to report as R7-style packaging, not a fault |
| C | **Challenge-local definitions that model the paper's objects.** A machine model, a lattice system, a code, written for the challenge. | it trusts the challenge file (assumption 1) | every challenge file;  by local-definition count (12 have none, 157 have 1–10, 214 have 11–50, 35 more than 50) | M3:  list them;  a person reads them against the paper, largest first | 4 read (`results/M3-readings.md`) |
| D | **Assumptions in the statement.** Hypotheses or typeclass arguments that carry the hard part, or that cannot be met. | the statement is the statement:  a conditional is checked as a conditional | the challenge statements' binders | L2 (unbuilt / carries a proposition), L3 (refuted on file), on the challenge side | CharacterVarieties:  a `Diagram` structure carrying propositions (L2 REVIEW) |
| E | **Coverage.** The paper claims more than the listed `theorem_names` state. | it checks only what is listed | scope notes (`lean/docs/*.md`) that say a part is "outside" or "not included";  the static scan found 91 such notes | read each note against its configuration's `theorem_names` | Cartier and CharacterVarieties:  supporting lemmas, headline outside (their notes say so) |
| F | **Statements weaker than the headline in the same file.** An `∃` where the paper means `∀`, a fixed size where it means every size, a quantifier moved. | equal statements, whatever they say | challenge theorems against the paper's abstract | a person, helped by the dictionary (M3);  R2/R4 once targets are registered | not yet searched |
| G | **Toolchain and dependency trust.** Assumption (1) covers the lakefile;  openai/math's lakefile patches dependencies before building. | it trusts the lakefile | which packages are patched, and whether any challenge imports one | static:  challenge files import only Mathlib (416) or `OAI` (2);  patched packages are not Mathlib | no challenge imports a patched package directly;  to confirm transitively for the 2 `OAI` ones |
| H | **Kernel or sandbox.** Assumptions (3–5). | it is the trusted base | — | independent kernels | already rechecked by others (nanoda, con-leche;  Lean Zulip) |

## 4. The narrowed search

From the table, the places to look, in order:
1. **The 2 `OAI`-importing challenges** (A):  done;  the slide is there.
2. **The 1 definition hole** (B):  read `PermutationWitness`;  report what the theorem adds over the witness.
3. **The 35 challenges with more than 50 local definitions, then the 214 with 11–50** (C):  the dictionary, read
   against each paper, largest first.
4. **Every challenge statement's hypotheses** (D):  L2/L3 on the challenge side (`run_all.py --side=challenge`).
5. **The 91 scope notes that say something is left out** (E):  the claim left out, beside the theorem kept.
6. **Quantifier and size checks** (F):  for the headline results the papers name, the statement written independently
   and registered as a target, then R2/R4.

Tracking meaning to statement:  for each challenge, the row is (paper's claim) → (configuration's `theorem_names`) →
(statement) → (the definitions its meaning rests on, by origin:  library, challenge-local, solution-side, hidden) →
(hypotheses).  A slide is recorded only where a step changes the claim and the change is shown from the files.
