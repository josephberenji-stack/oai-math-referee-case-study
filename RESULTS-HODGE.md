# Results: the Hodge configuration and its 33,169-module closure

Author:  Joseph Berenji.

This file reports the claims registered in `PREREG.md` for the Hodge configuration ("The Hodge configuration", H1–H5; "The new referee checks", N1–N4). It sets two things side by side: what Comparator, the Lean FRO's checker, reports about the submission, and what the Lean referee of Discipline-Architecture-2 reports about the same theorem. Every verdict below quotes the published file it rests on. Sections 1–3 are the registered claims. Section 4 is exploratory and not registered, and is labelled as such.

## 0. What was checked

- **The configuration.** `ComparatorChallenges/HodgeConjectureCMAbelianVarieties/main.json` in openai/math at `7ef5c0cc`: one theorem, `HodgeCM.hodge_conjecture_for_cm_abelian_varieties`, permitted axioms `propext`, `Quot.sound`, `Classical.choice`.
- **The solution's theorem is a wrapper.** The whole proof in `Solution.lean` is `OAI.AlgebraicGeometry.HodgeConjecture.MainSolution.hodge_conjecture_for_cm_abelian_varieties X hCM p`. So the referee's rows on that `MainSolution` theorem are the rows on the substance of the submission.
- **Comparator.** Run on `main.json` unchanged: `results-hodge/comparator/HodgeConjectureCMAbelianVarieties.out`.
- **The referee on the configuration** (`results-hodge/HodgeConjectureCMAbelianVarieties/referee.out`) stopped at Lean's default step limit inside the referee's own commands: `BUILD FAIL … maximum number of heartbeats (200000) has been reached`. That is a limit of the referee, fixed in DA-2 PR #16 (see `results-hodge/closure/rerun-2026-11-03-hb/README.md`).
- **The referee on the closure.** All 33,169 `OAI` modules and the 257 `HodgeConjecture` helper files, in 2,181 groups (`results-hodge/closure/`). The 10 groups that hold the top of the proof were rerun with the step-limit fix (`results-hodge/closure/rerun-2026-11-03-hb/`). `MainSolution` is in group 1199 of that rerun.
- **Deviation from the registration, stated.** PREREG registered the Hodge pass with DA-2 `e0854d5`. The closure run used DA-2 `6e33e0d`, the commit recorded on the machine; the rerun used `6e33e0d` plus the heartbeat patch. The check names in every output are those of `6e33e0d` (R1i, DUP, SHADOW, INST and VEND included). No claim or kill condition was changed.

## 1. The registered claims

| Claim | Verdict | The line it rests on |
|---|---|---|
| **H1** (L0): only the three axioms | **holds** | rerun group 1199, `MainSolution.hodge_conjecture_for_cm_abelian_varieties`: `L0 PASS [propext, Classical.choice, Quot.sound]` |
| **H2** (L1): no stand-in | **holds** | same theorem: `L1 REVIEW [opaque with a value …ProjectiveBasic.CochainComplex.wrapped…]`. This is the opaque wrapper of an `irreducible_def` (`IsKProjective.homotopyZero`), not a stand-in; the kill is an L1 FAIL, and there is none. |
| **H3** (Comparator): real Comparator accepts | **fails** | `comparator/HodgeConjectureCMAbelianVarieties.out`: `uncaught exception: Challenge and solution theorem statement do not match: 'HodgeCM.hodge_conjecture_for_cm_abelian_varieties'` (exit 1, 693 s, after `Build completed successfully (42093 jobs)`) |
| **H4** (origins): no `OAI`-declared definition in the statement | **fails** | `results-hodge/summary.tsv`: `solution_side_defs 435`, `challenge_local_defs 0`, `challenge_folder_helper_defs 0`; the 435 are listed in `origins.txt` |
| **H5** (census): nothing a person named left unclassed in the closure | **holds** | All 2,181 groups' census outputs (group 482 rerun on 6 Nov, `census/group-482.PROVENANCE.md`; the ten reruns from `rerun-2026-11-03-hb/census/`). The unclassed accepted theorems are 5,823, every one of a generated shape: `congr_simp` 3,647, `inj / injEq` 1,380, `sizeOf_spec` 711, `eq_def` 83. None is `other` or a person's `eq_` name. The configuration's own census (1 unclassed, `{'other': 1}`) is its referee BUILD FAIL, counted as BUILD FAIL under PREREG's 28 Oct rule. |
| **N1** (R1i): every input carries content (R1i PASS) | **fails** | group 1199, same theorem: `R1i REVIEW input supplied by unfolding alone: [ … ]` (six inputs, quoted in §3) |
| **N2** (SHADOW): the closure reaches a project copy of a library declaration (SHADOW REVIEW) | **fails** | same theorem: `SHADOW PASS no copy of a library declaration` |
| **N3** (VEND): every module under `HodgeConjecture/Mathlib/` is VEND REVIEW | **holds** | closure groups 51–71: 28 of 28 such modules `VEND REVIEW` |
| **N4** (INST): `GeometricAlgebraicity` is INST REVIEW | **holds** | rerun group 675: `INST OAI.AlgebraicGeometry.ComplexMultiplication.Reference.GeometricAlgebraicity REVIEW instance changes at lines 18` |
| Recorded: DUP on the theorem | REVIEW | group 1199: `DUP REVIEW twins without a proved equivalence: [ … ]`, six pairs (e.g. `PicardOpenImmersionGluing.isoOnRange = NeighborCounting.OpenImmersionGluing.isoOnRange`) |
| Recorded: L2 on the theorem | REVIEW | `IsIntegral`, `Smooth`: side conditions; `IsProjective`, `HasComplexMultiplication`: **carries a project proposition** (both are `OAI`'s own definitions) |
| Recorded: class | A? | `CLASS REVIEW computed class A?` |

Held: H1, H2, H5, N3, N4. Failed: H3, H4, N1, N2.

## 2. What Comparator saw, and what it did not unpack

Comparator answers one question: is the solution's theorem the challenge's theorem, using only the permitted axioms? On this configuration it answered **no**, in one line, without saying where the two differ.

The difference is in the source, and the origins pass makes it exact:

| | `Challenge.lean` | `Solution.lean` |
|---|---|---|
| projectivity | `IsProjective X.hom` | `OAI.AlgebraicGeometry.Foundations.ProjectiveSpaceIs.IsProjective X.hom` |
| complex multiplication | `HasComplexMultiplication X` | `OAI.AlgebraicGeometry.ComplexMultiplication.Definitions.HasComplexMultiplication X` |
| the right-hand side | `algebraicCycleClassSpan X p` | `OAI.AlgebraicGeometry.ComplexPoint.Basic.ComplexSchemePoint.algebraicCycleClassSpan X p` |
| definitions the statement reaches | the challenge folder's own (`CM.lean`, `HodgeConjecture/`) | **435 `OAI` definitions, 0 from the challenge folder** (`summary.tsv`) |

The names match and the constants do not. The solution proves a theorem about its own objects.

**What the `OAI` versions say.** Each is a copy of the challenge's definition, with the same text, moved into the `OAI` namespace (source at `7ef5c0cc`):

| | the challenge (`ComparatorChallenges/HodgeConjectureCMAbelianVarieties/`) | the solution's library |
|---|---|---|
| `IsProjective` | `HodgeConjecture/Definitions/AlgebraicGeometry/ProjectiveSpace.lean:147` | `OAI/AlgebraicGeometry/Foundations/ProjectiveSpaceIs.lean:147` (header line 15: "This file has been modified.") |
| `HasComplexMultiplication` | `CM.lean:55`, `Nonempty (CMH1Data X)` | `OAI/AlgebraicGeometry/ComplexMultiplication/Definitions.lean:57`, `Nonempty (CMH1Data X)`, with the same `CMH1Data` text |
| `algebraicCycleClassSpan` | `HodgeConjecture/Definitions/AlgebraicGeometry/Cycle/FundamentalClass.lean:146` | `OAI/AlgebraicGeometry/Cycle/FundamentalClass.lean:153` (header line 4: "This file has been modified."), with the same `sSup` of spans of fundamental classes |

The bodies read the same, but each is built on the library's own copies of the objects beneath it: rational and de Rham cohomology, the Hodge filtration, the fundamental classes. **No `OAI` file imports the challenge folder** (`grep -rlE '^(public )?import HodgeConjecture' OAI` finds 0 files). So no theorem in the library can state, let alone prove, that its copy is the challenge's definition. The two vocabularies are parallel and never joined, and that is what Comparator's "do not match" detects.

Comparator could not have said more, because it compares statements and lists axioms; it does not open the definitions or the proof. The referee does both. On the same theorem it reports, with the line for each:
- **the hypotheses that are the library's own propositions** (L2: `IsProjective`, `HasComplexMultiplication` "carry a project proposition");
- **the inputs supplied by unfolding a definition rather than by a proof** (R1i, six of them);
- **twin definitions used without a proved equivalence** (DUP, six pairs);
- **hidden values** (L1: the `irreducible_def` opaque);
- **a module that removes an instance** (INST, `GeometricAlgebraicity`);
- **project files stored under a `Mathlib/` folder** (VEND, 28 modules);
- and, over the closure, the same for every one of 33,426 modules, with a class for every theorem (`results-hodge/closure/`).

Comparator also never ran this configuration in openai/math's own pipeline as far as the files show: it sits in a subfolder, not with the 418 configurations at the top of `ComparatorChallenges/` (noted in PREREG before the run). That is a reading of the folder layout, not a confirmed fact about OpenAI's process.

## 3. Answered by construction, not by solution: what the referee shows

The question is whether the theorem settles the challenge's statement, or a statement the library constructed for itself. Three registered measurements bear on it:

1. **The statement is the library's own (H4 fails).** All 435 definitions the solution's statement reaches are declared in `OAI` modules, and none in the challenge folder. The challenge's definitions are not used at all.
2. **The hypotheses are the library's own propositions (L2).** `IsProjective` and `HasComplexMultiplication` in the solution are `OAI` definitions, flagged "carries a project proposition".
3. **Inputs are supplied by unfolding, not proved (N1 fails, R1i REVIEW).** Six inputs the proof needs are discharged because a definition unfolds to them:
   `WeightOne.CM.RankOneCMAction` by `Decomposition.CM.CMComponent.cm`;
   `PELModuli.IntegralModel.Components.RelativelyProjective` by `CMExtraction.ReferenceAlbanese.Intrinsic.singleBaseComponentVariety._proof_7`;
   `Scheme.Constructions.Foundations.FinitePresentationMorphism` by `ModelFiniteness.Constructions.Foundations.baseChange_finitePresentation`;
   `PELModuliCandidate.ClassifiesReduced` by `SphericalPELAlbaneseData.HasIntegralModelGeometry.classifies`;
   `CMVariety.AbelianEndomorphism.ConjugateAbelianTuples` by `AbelianEndomorphismTuple.conjugate_comparison`;
   `Blowups.Smooth.ControlPrefix…HasIncidenceTrace` by `UniformControlProgramSystem.hasTrace`.

None of this says the proof is wrong: the kernel accepts it, with the three axioms (H1). It says what was proved: a statement built from the library's own definitions, with some inputs met by how those definitions were built. That is "by construction". Comparator's mismatch (H3) is the same fact seen from outside.

## 4. Exploratory (not registered): the shape of the closure

These measurements were made after the run, on the published closure and on the source at `7ef5c0cc`, by the scripts in `analysis/hodge-closure/`. They were not predicted in PREREG and decide no claim. They are given because they show where the construction sits.

- **The top of the proof routes; it does not argue.** `CMReduction.Established` supplies the twelve named inputs of the final step, each as one line naming a proof elsewhere. `CMReduction.Core` is one line. `MainSubmission` declares nothing; its only role is to fix the import order of two Mathlib modules that export the same instance names. `MainSolution` is five lines.
- **One input carries the library.** 25,526 of the 33,168 files under `MainSubmission` are needed only by the input `switches` (four-factor switch algebraicity), through `SurfaceConstructionCycle` (`deep.out`).
- **Restated goals, compared with Mathlib** (same script on both; `proofs-baseline.out`). The tactic `change`, which restates a goal as a definitionally equal one, appears in 23.8% of the closure's 107,747 proofs and 0.7% of Mathlib's 187,302. The median proof is 6 lines against 2. Automation appears in 19.5% against 28.3%.
- **Deeper definitions** (`nest.out`; name resolution by text, ambiguous names skipped on both sides). The chain of definitions a definition rests on has median 4, p99 31 and maximum 57 in the closure, against 3, 21 and 39 in Mathlib. The deepest chain ends at `StableHilbert.GluedPolarizedFamily`.
- **The statement's definitions sit in the wide base** (`origins_depth.out`). Of the 435 `OAI` definitions the statement reaches, 356 map to a module with a recorded depth (79 sit in modules with no theorems and are not placed). Their depth has median 2, p90 15 and maximum 31; the proof's top file is at depth 189. The objects the theorem speaks about are built at the bottom of the library, and everything above them routes toward the statement.
- **The library copies the challenge's whole vocabulary, except its statement** (`copies.out`, `copies.tsv`; matching by declaration name, then text similarity after the namespaces are stripped). The challenge folder's 257 helper files and `CM.lean` declare 2,907 names. **2,906 of them have an `OAI` declaration of the same name.** The one that does not is `HodgeConjecture` in `HodgeConjecture/Statement.lean`, the statement of the Hodge conjecture itself. File by file, 45 helper files reappear in `OAI` with the same text (similarity ≥ 98% after renaming) and 66 more nearly so (80–98%). The rest are spread or reworded, and 213 of the files' names land in a single `OAI` file. Name matching does not prove the bodies agree; it locates the copies, and the similarity column measures how close they are.
- **Declaration by declaration, the copies agree with the originals in text** (`agree.out`, `agree.tsv`, scripts `agree.py`, `agree2.py`). The 2,909 helper declarations were compared with their `OAI` namesakes, statement and body, with namespaces stripped and qualified names reduced to their last component. **2,423 (83.3%) have the same statement and the same body**, 104 (3.6%) the same statement with a different proof, 381 (13.1%) a different statement, and 1 no namesake (the conjecture's statement). The sampled "different statement" rows differ by renaming only, e.g. the type `ComplexPoint` written `Basic.ComplexSchemePoint`, so 83.3% is a lower bound. Text agreement is not identity: each copy is elaborated against the library's own copies of the objects beneath it, and no theorem equates a copy with its original (§2).
- **Gluing** (`choice.out`). 2.11% of the closure's definitions glue or descend, against 0.21% of Mathlib's.

## 5. Limits

- The verdicts on H1, H2, N1, N2, DUP and L2 are read on `MainSolution.hodge_conjecture_for_cm_abelian_varieties`, which `Solution.lean`'s theorem wraps (§0). The configuration's own referee pass did not produce rows (step limit), and was not rerun: that needs the full closure built again.
- The referee version differs from the registered one (§0).
- Comparator was run by us, on `main.json` unchanged; the statement difference in §2 is visible in openai/math's own source either way.
- §4 is exploratory, and its name resolution is textual.
- Nothing here judges whether the mathematics is new or correct beyond what the kernel checks.
