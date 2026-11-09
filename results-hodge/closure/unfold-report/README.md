# The unfold report over the closure (the package checks UNFOLD, BRIDGED, CARRIER)

`unfold_report.py` of Discipline-Architecture-2 at `6e33e0d4b57af8e8f0db01dec5880bbd9a41a840` (the closure run's referee),
run on 6 Nov 2026 on a Mac over the published unfold files. Inputs:
- `../unfold/`: 2,181 groups, with the ten groups in `../rerun-2026-11-03-hb/unfold/` in place of their originals;
- `--library=library-mathlib.tsv`: the outside library's structures (Mathlib at openai/math's pin, 2,253 structures),
  written by `referee_lean.py --unfold-library` in openai/math at `7ef5c0cc` on Lean 4.34.1.

Run: `python3 unfold_report.py --in=<one folder holding every *.unfold.tsv> --library=library-mathlib.tsv --out=<dir>`.
It took 31 s and 10.9 GB of memory. Exit 0.

| File | What |
|---|---|
| `summary.md` | the counts |
| `checks.tsv.gz` | every package-check row (UNFOLD, BRIDGED, CARRIER) |
| `carriers.tsv` | each carrier (a project proposition used as a hypothesis, or a proposition field read by a proof), with the theorems that use it and whether it is established on file |
| `counterparts.tsv` | each project structure and class, with outside-library instances and the closest outside-library structures by field names |
| `inventory.tsv`, `decls.tsv.gz`, `r1k.tsv.gz` | per module, per declaration, per theorem (gzip, to stay under GitHub's file size limit) |

**Results** (`summary.md`): 173,870 declarations, 111,651 of them theorems.
- **UNFOLD PASS: 33,426 modules.** Every theorem is accounted for in the unfold map.
- **R1k, what carries each theorem:** CONTENT 110,618; UNFOLD 627; FIELD 330; IND 52; HYP 24.
- **CARRIER:** PASS 608, **REVIEW 219**. A REVIEW is a project proposition that theorems assume and no theorem establishes.
  The inputs of the Hodge proof's final step (for example `CMReduction.…LineBundleCyclesInput`, `ExteriorInput`, `PolarizedPairingInput`, `FunctorialityInput`) are listed as **established** in `carriers.tsv`.
- **BRIDGED:** INFO 110,618, PASS 753, **REVIEW 280**. A REVIEW is a theorem without content about a project type that already carries an outside-library instance: proved by unfolding while the bridge to Mathlib sits unused.

These checks change no theorem's class.
