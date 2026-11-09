# K4 (L1u), interim reading on the three families built so far (28 Oct 2026)

K4 as amended before any L1u run: every `opaque` reached by a challenge theorem is reached only from its proof, never
from the challenge statement. Kill: one `statement:*` row for a challenge theorem.

| family | challenge theorem | L1u | opaque constants |
|---|---|---|---|
| PeriodicGroup | `OAI.SourceBurnside.thm_main` | PASS, proof-only | `SourceMachine.coding`, `SourceMachine.localCircuit` |
| OddKaplansky | `OAI.OddKaplansky.main_theorem` | PASS, proof-only | `GraphNumerics.binomWrapped`, `SourceGluing.pWrapped` |
| CharacterVarieties | `…Diagram.producedMarkedValues_allSeams` | REVIEW, statement-level | `Diagram.cutGeneratorWitness` |

**K4 fails on CharacterVarieties.** This is one of the few challenges whose challenge file imports OpenAI's own library
(`import OAI.AlgebraicGeometry.CharacterVarieties.Seams.ProducedEquations`). Its statement,
`D.ProducedMarkedSeamEquations q hproper hmax hg P x b0 i0`, is an OpenAI definition, and that definition's meaning
reaches the `opaque` `cutGeneratorWitness` (`Frames/MarkedFrames.lean:18`). Comparator checks the solution against
this statement, but the statement's content is partly inside the hidden value. A person has to read
`cutGeneratorWitness`'s value to know what the theorem says. This is a REVIEW, not an error in the proof.

Other theorems in the same modules (not challenge theorems) reach opaques from their statements too (the
`*_reference` lemmas in PeriodicGroup, the `Prescribed.*` lemmas in OddKaplansky); K4 does not cover them.

Raw rows: `results/*/referee-L1u.out`. Referee: Discipline-Architecture-2 at 474014d.
