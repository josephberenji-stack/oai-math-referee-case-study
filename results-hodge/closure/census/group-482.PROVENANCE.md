# Group 482's census: rerun on 6 Nov 2026

The closure run's `census/group-482.out` was empty (0 bytes), and `census/group-482/` was missing, although `referee/group-482.out` holds its 123 CLASS rows. The census was rerun after the run's machine had stopped:

- **Machine:** a Mac, with openai/math at `7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a`. The group's 482-module `OAI` import closure was compiled one file at a time with `scripts/build_seq.py --mem=16384`, toolchain leanprover/lean4:v4.34.1 (the library's own).
- **Census:** Discipline-Architecture-2 at `6e33e0d4b57af8e8f0db01dec5880bbd9a41a840` (the closure run's commit), `discipline/lean/census/census.py --project=<lean dir> --modules=<the 25 modules of group 482 in GROUPS.tsv> --out=census/group-482 --referee-log=referee/group-482.out`, with `DISCIPLINE_LEAN_REGISTRY=results-hodge/closure/registry.tsv`.
- **Result:** exit 0. `CENSUS stated 156, stated theorems 123, accepted user 158, accepted theorems 125, generated 77, stated-not-accepted 0, accepted-not-stated 2`. Unclassed: 2, both `congr_simp`.
- **Not rerun:** the referee. `referee/group-482.out` is the closure run's own file, unchanged.
