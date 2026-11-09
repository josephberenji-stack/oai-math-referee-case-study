# Exploratory analysis of the Hodge closure (not registered)

This is section 4 of `RESULTS-HODGE.md`. These scripts read openai/math at `7ef5c0cc` and the published closure results (`results-hodge/closure/`). They were run after the closure run, on the machine that ran it, and they decide no registered claim.

| Script | Output | What it measures |
|---|---|---|
| `spine.py` | `spine.tsv` | the longest import chain from `MainSubmission` down (190 files), with referee rows per file |
| `found.py` | `found.out` | the files most others rest on, file sizes, imports per file |
| `deep.py` | `deep.out` | the conclusion type of each theorem for the 18 inputs of `CMReduction.Established`, the files only one input needs, and the subtree of the final step |
| `rfl.py`, `rflsort.py` | `rfl.out`, `rflsort.out` | theorems proved by `rfl`, sorted by text into projections, unfoldings and candidate identifications |
| `proofs.py`, `proofs2.py` (with `mklist.py`) | `proofs.out`, `proofs-baseline.out` | proof length and tactic use, for the closure and for Mathlib at the closure's pin |
| `nest.py` | `nest.out`, `fanout.out` | how many layers of definitions a definition rests on, for the closure and for Mathlib (names resolved by text; ambiguous names skipped) |
| `choice.py` | `choice.out` | definitions built by choice, and definitions that glue or descend, for the closure and for Mathlib |
| `copies.py` | `copies.out`, `copies.tsv` | which challenge helper declarations reappear in `OAI` under the same name, and how close each file's text is |
| `agree.py`, `agree2.py` | `agree.out`, `agree.tsv` | statement and body agreement of each helper declaration with its `OAI` namesake |
| `reach.py` | (prints) | the constants one theorem reaches, from the unfold layer |

The `.tsv` per-row outputs (`rfl.tsv`, `rflsort.tsv`, `nest-*.tsv`) are reproducible from the scripts and are not committed here.

To run:  the scripts read `CLOSURE_DIR` (default `/srv/oai/casestudy/results-hodge/closure`, the run machine's copy of
`results-hodge/closure/`), `SRCS` (a list of each module's source path, in `MODULES.txt` order) and, where they write a
table, `OUT_TSV`;  the scripts that read source take the two source roots `sources/openai-math/lean` and
`sources/openai-math/lean/ComparatorChallenges/HodgeConjectureCMAbelianVarieties` as arguments.  `copies.py`, `agree.py`,
`agree2.py` run from `sources/openai-math/lean` with an output path as their argument;  `origins_depth.py` takes
`rfl.tsv` and `origins.txt`.
