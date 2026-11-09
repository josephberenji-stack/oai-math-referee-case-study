# Solution-side referee, second pass (31 Oct 2026)

After the full run (ea4508e), 114 of the 545 challenge theorems had no CLASS row in `results-full/summary.tsv`
(latest row per challenge and theorem; the file only appends, so a rerun adds rows rather than replacing them).

Causes, and what was run on oai-run:

1. **109 theorems declared outside the solution module.** `run_all.py` gives the referee the challenge's
   `solution_module`, and the referee checks only the declarations of the module it is given. Lean
   (`Environment.getModuleIdxFor?`, `declmod.py`) places each of these 109 in a sibling module of the same folder
   (68 challenges, 88 modules). `refdecl.py` ran the same referee, registry and memory cap on each declaring module.
   Results: `declmod-rows.tsv` (every row for each target theorem), `referee/<module>.out`. All 109: L0 PASS;
   CLASS 106 `A?`, 3 `C`.
2. **4 challenges never rerun.** `--skip-done` skipped AmplitudeDamping, ArtinCAT0, AuslanderReiten and
   BalancedBoxRouting because their 29 Oct `meta.json` (written while the disk was full) still existed. Their old
   folders were moved to `/srv/oai/stale-20261029` on the VM, and `run_all.py --only=…` reran them; the new folders
   are in `results-full/`, their rows appended to `summary.tsv`. All four: CLASS `A?`.
3. **1 theorem skipped by the referee.** `OAI.PinchedHartogs.controlled_potential` (PinchedKahler) is a theorem of
   the walked module, but the referee's generated-name filter dropped every name starting with `control`. Fixed in
   Discipline-Architecture-2 (branch fix-control-filter, PR #4). Rerun on oai-run with the run's own referee (a98736b)
   and only that rule removed: `control-fix/OAI.Geometry.Kahler.Main.out`, "2 theorems checked";
   `controlled_potential` L0 PASS, CLASS `A?`.

With these, all 545 challenge theorems have a CLASS row: 531 `A?`, 14 `C`.

Files: `unclassed.tsv` (the 114), `declmod.tsv` (declaring module of each), `declmod.py`, `refdecl.py`, `refdecl.log`.
