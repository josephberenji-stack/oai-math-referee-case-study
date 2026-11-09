# Case study: a Lean referee on the openai/math formalizations

This repository applies the Lean referee of Discipline-Architecture-2 (`discipline/lean/`) to the Lean library
published at github.com/openai/math, commit `7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a` (26 Oct 2026). The version of
the referee that was run, commit `6e33e0d`, is published at github.com/josephberenji-stack/discipline-architecture-2-referee.

The Lean kernel checks that the proofs are correct, and Comparator, the Lean FRO's checker that openai/math's
challenge configurations are written for, confirms that each solution matches its challenge statement and uses only
`propext`, `Quot.sound` and `Classical.choice`. (For the Hodge
configuration, Comparator reports that the two statements do not match: `RESULTS-HODGE.md`, H3.) This study asks a
further question about each accepted theorem: what the checked statement says, where the meaning of its definitions
comes from, and whether that is the claim of the paper.

Results are in `RESULTS.md` (the 418 challenges) and `RESULTS-HODGE.md` (the Hodge configuration and its closure:
33,169 `OAI` modules and 257 helper files, 33,426 modules in all). The claims were written down before each measurement, in `PREREG.md`.

Paths under `/srv/oai/` in scripts and logs are those of the machine the runs were made on. The runs were made from a
private working repository, `lean-referee-case-study`, whose name and commits appear in the logs and in
`scripts/oai-vm.sh`. This repository is its published copy. Every run's results are here. Five working files of the
run machine are not: a duplicate log folder, the run plan, unused split-rerun scripts, an unfinished export and a
watcher's log.

## Layout

    PREREG.md            the claims (K1–K5, M1–M4), with one dated amendment and one dated revision
    RESULTS.md           what held, what failed, and the limits
    scripts/             static_scan.py (token scan, nothing run), build_seq.py (capped one-file-at-a-time build),
                         StmtOrigins.lean.tmpl (where a statement's definitions are declared)
    scans/               the static scan of the whole library
    referee/             the registries the referee ran with
    results/             one folder per family (referee, census), and the M1–M4 / K4 write-ups
    results-hodge/       the Hodge configuration: referee, census, origins, Comparator; closure/ holds the referee,
                         census and unfold output of all 2,181 groups of the 33,426-module closure, and
                         closure/rerun-2026-11-03-hb/ the ten groups rerun with the step-limit fix (its README)
    analysis/            exploratory measurements, not registered (analysis/hodge-closure/README.md)
    benchmark/           the planted-fault benchmark (our files) and the reimplemented Comparator checks
    logs/                the build logs
    sources/             the upstream clone (not committed)

## Reproducing

1. Clone github.com/openai/math at the commit above into `sources/openai-math`. In `sources/openai-math/lean`, run
   `lake exe cache get` (this runs their lakefile, which clones and patches its dependencies).
2. Build a challenge's solution module one file at a time with a memory cap:
   `python3 -I scripts/build_seq.py sources/openai-math/lean <solution module> --mem=8192`.
3. Run the referee from Discipline-Architecture-2 with this repository's registry:
   `DISCIPLINE_LEAN_REGISTRY=referee/registry.tsv python3 <DA-2>/discipline/lean/referee_lean.py
   --project=sources/openai-math/lean --modules=<solution module>`, then its census the same way.
4. The benchmark needs only Mathlib. Build `benchmark/Defs.lean`, `Challenge.lean` and `Solution.lean` in any Lean
   project with Mathlib, run `Compare.lean`, and run the referee on the solution with `referee/registry-bench.tsv`.
5. The Hodge closure. The groups are listed in `results-hodge/closure/GROUPS.tsv` (group, module). Each group was
   refereed with `python3 -I <DA-2>/discipline/lean/referee_lean.py --project=<lean dir> --modules=<the group's
   modules, comma-joined> --unfold-out=<out>/unfold/group-K`, and the census was then run with `--referee-log` set
   to that output, as in `results-hodge/closure/rerun-2026-11-03-hb/rerun-hodge.sh` (the one-group script). The
   referee was DA-2 at `6e33e0d` with registry `results-hodge/closure/registry.tsv`; the ten reruns add the patch in
   that folder. The driver script for the whole closure run is `scripts/oai-hodge-vm.sh`. The one-group script runs
   the same command for each group.

Toolchain: OpenAI's library uses Lean 4.34.1. The benchmark was run on 4.33.1.

## The referee version, and what the closure run did not get

The Hodge closure was refereed with Discipline-Architecture-2 at `6e33e0d4b57af8e8f0db01dec5880bbd9a41a840`. The ten
groups in `results-hodge/closure/rerun-2026-11-03-hb/` used that commit plus the step-limit patch in that folder. The
referee changed afterwards, and none of the later changes below are in these results:

| DA-2 change (pull request, date) | What it does | What it would affect here |
|---|---|---|
| CARRY row (#10, 1 Nov) | flags a conclusion carried in by hand, as a hypothesis or a declared model choice | statements whose content is assumed rather than proved |
| IFFSET row (#11, 2 Nov) | set equations; logic and membership lemmas count as no content for IFF and IFFSET | rows for set equalities and iffs |
| source lookup under a `srcDir` (#13, 2 Nov) | finds a module's source outside the main folder, or reports SRC FAIL | L4–L6 for files under `ComparatorChallenges/…/HodgeConjecture/` |
| generated names (#14, 2 Nov) | skips what `@[ext]` writes and `ofNat_ctorIdx` | the census's unclassed counts |
| R1 instance fix (#15, 3 Nov) | a project instance counts as plumbing, like a library one | R1 and class DEF where a proof only passes instances |
| step limit 4,000,000 for the referee's own commands (#16, 3 Nov) | applied to the ten reruns only | the other 2,171 groups did not reach the old limit |
| module manifest (#17, 4 Nov) | tracks sections and ignores block comments | L4 and L6 |
| `Set` naming (#18, 6 Nov) | names `Set`, `Set.ofPred` and `setOf` without resolving them | statements about sets |

The package checks UNFOLD, BRIDGED and CARRIER existed at `6e33e0d` (`unfold_report.py`). They were run later, on
the published unfold files, at the same commit: `results-hodge/closure/unfold-report/`. The referee's self-test and
mutations at `6e33e0d` on Lean 4.34.1, and a reproduction of one group on a second machine (2,364 of 2,364 rows
identical), are in `results-hodge/closure/referee-checks/`.

The referee's list of compiler-generated names is pinned to Lean 4.33.1 (DA-2 README §25), while openai/math uses
4.34.1. Over the closure, every accepted theorem that the census found unclassed has a shape on that list
(`congr_simp`, `inj / injEq`, `sizeOf_spec`, `eq_def`), and none has the shape `other`. The 135 theorems with a
hand-written name starting `eq_` were all read (`analysis/hodge-closure/name-shapes.out`). The list held on this
toolchain for this library.

## How this was made

Joseph Berenji designed and directed this study: the questions, the claims registered before each run, and what
counts as a result. The scripts, the Lean files and the text of this README and of the result files were written by
Claude (Anthropic), working in Claude Code to his instructions. Every number in the results is read from an output
file in this repository.

## Licence

Apache License 2.0 (`LICENSE`, `NOTICE`). No file of openai/math is redistributed here.
