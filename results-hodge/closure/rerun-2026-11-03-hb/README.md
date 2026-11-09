# Hodge closure: heartbeat-fixed reruns of the 10 top groups (3–6 Nov 2026)

A published test case of the referee's mechanics: what was rerun, with which referee and command, on which toolchain,
what came out, and how to check each file.

## What was rerun and why

The closure run (`../referee/`, `../census/`, `../unfold/`) checked 33,426 modules of openai/math in 2,181 groups. Ten
groups ended `REFEREE BUILD - FAIL`, so they have no rows. They are the groups that hold the top of the Hodge spine:
675 1128 1129 1134 1154 1192 1199 1200 1201 1736 (`GROUPS-RERUN.txt`, second column = Lean memory cap in MB).

- In the closure run (`../referee/group-K.out`), nine of them failed on memory: `lean exited 134: libc++abi:
  terminating due to uncaught exception of type lean::memory_exception: excessive memory consumption detected at
  'interpreter'` (675 1128 1129 1134 1192 1199 1200 1201 1736). Group 1154 failed on the step limit:
  "(deterministic) timeout at `whnf`, maximum number of heartbeats (200000) has been reached".
- The first rerun (`../rerun-2026-11-03/`, the unchanged referee, a larger memory cap) got past the memory failure in
  all ten. Every one then stopped at the referee's own commands (`#referee`, `#referee_module`), after the modules
  themselves had built, on Lean's default step limit: "(deterministic) timeout at `whnf`" (`isDefEq` in 1199),
  "maximum number of heartbeats (200000) has been reached" (`../rerun-2026-11-03/referee/group-K.out`, each
  `BUILD FAIL`).

This folder is the rerun of all ten with both fixed: a 32 GB memory cap (`-M32768`) and a finite but larger step limit
(4,000,000) for the referee's commands.

## Referee

`/srv/oai/da2-hb` on the VM: Discipline-Architecture-2 at `6e33e0d4b57af8e8f0db01dec5880bbd9a41a840` (the VM's
`da2-commit`, the commit of the closure run) plus the heartbeat fix. The fix is the `referee_lean.py` hunk of DA-2
commit `d83968be978b3e3ceee7173443971e89434646e5` ("referee: a finite step limit for its own commands (4,000,000;
REFEREE_HEARTBEATS)", 2026-11-03 19:33:40 UTC, PR #16, merged to DA-2 main as `f31b120a79`). It sets
`set_option maxHeartbeats ${REFEREE_HEARTBEATS:-4000000}` before the referee's commands. The commit is in
`referee-heartbeat-fix-d83968be.patch`.

How we know the base is 6e33e0d and not d83968be's own parent `c90b4dc1`: c90b4dc is 12 commits ahead of 6e33e0d, and
those commits add the CARRY and IFFSET rows. No file in this folder has a CARRY or IFFSET row. The check names here are
exactly those of the closure run (CLASS DUP IFF INST L0 L1 L1u L2 L3 L4 L5 L6 MODULE R1 R1i R1k R2–R7 SHADOW VEND).
The `/srv/oai/da2-hb` tree itself was not copied off the VM before it stopped.

To rebuild the referee: check out DA-2 `6e33e0d` and apply the `discipline/lean/referee_lean.py` part of the patch
(`git apply --include=discipline/lean/referee_lean.py referee-heartbeat-fix-d83968be.patch`).

## Command

`rerun-hodge.sh K MEM` (in this folder), run once per line of `GROUPS-RERUN.txt` with MEM = 32768:

```
python3 -I /srv/oai/da2-hb/discipline/lean/referee_lean.py --project=. --modules=<group K's modules> \
  --unfold-out=unfold/group-K > referee/group-K.out 2>&1;  echo "exit $?" >> referee/group-K.out
python3 -I /srv/oai/da2-hb/discipline/lean/census/census.py --project=. --modules=<...> --out=census/group-K \
  --referee-log=referee/group-K.out > census/group-K.out 2>&1;  echo "exit $?" >> census/group-K.out
```

with `DISCIPLINE_LEAN_REGISTRY=../registry.tsv`, `REFEREE_MEM=32768`, run from `/srv/oai/closure-root` (the closure
project). Each group's modules are the rows of `../GROUPS.tsv` with that group number. Each group is one Lean process
(`lake env lean -M32768 -j2`) on one core.

## Toolchain

- Lean `leanprover/lean4:v4.34.1`
- openai/math `7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a` (`lean/` is the project)
- Mathlib `d13f23b723b8` (openai/math's `lake-manifest.json`)
- VM `oai-hodge`, n2-highmem-64, europe-west1-b, Ubuntu 24.04

## Times

`TIMES.tsv`. Wall time from start to the referee's `exit` line, in hours: 1154 8.3, 1201 12.0, 1200 13.8, 1128 17.7,
1192 19.7, 1129 22.7, 675 27.0, 1736 28.3, 1134 30.5, 1199 40.1. A start time marked "observed" was read on the VM
from the process's elapsed time. The others are from the VM handoff of 4 Nov. End times are the files' modification
times, kept by tar when copied off the VM. For 1199 the end time is the first one-minute poll that saw `exit`.

## Results

Counted from `referee/group-K.out`. The full tables, every CLASS row for the spine names and every non-L6 FAIL row
with its detail are in `SUMMARY-2026-11-06.md`.

| group | .out md5 | last line | CLASS rows | PASS | REVIEW | FAIL | class A? | class C | class DEF | FAIL rows by check |
|---|---|---|---|---|---|---|---|---|---|---|
| 675 | 71bf4619 | exit 1 | 69 | 0 | 69 | 0 | 69 | 0 | 0 | L6 25 |
| 1128 | 5c2f4b57 | exit 1 | 64 | 1 | 63 | 0 | 63 | 0 | 1 | L6 25, R1 1 |
| 1129 | fb542fde | exit 1 | 102 | 3 | 99 | 0 | 99 | 0 | 3 | L6 25, R1 3 |
| 1134 | 17e78c00 | exit 1 | 48 | 0 | 48 | 0 | 47 | 1 | 0 | L2 1, L6 12 |
| 1154 | 6d28e6c5 | exit 1 | 65 | 0 | 65 | 0 | 63 | 2 | 0 | L2 2, L6 17 |
| 1192 | f152d633 | exit 1 | 86 | 1 | 85 | 0 | 84 | 0 | 2 | L6 25, R1 2 |
| 1199 | 20109aff | exit 1 | 86 | 1 | 85 | 0 | 76 | 9 | 1 | L2 9, L6 25, R1 1 |
| 1200 | 05ba8aae | exit 1 | 39 | 2 | 37 | 0 | 37 | 0 | 2 | L6 6, R1 2 |
| 1201 | 58cb11d5 | exit 1 | 131 | 1 | 130 | 0 | 126 | 4 | 1 | L2 4, L6 25, R1 1 |
| 1736 | 0f9ab3da | exit 1 | 108 | 1 | 107 | 0 | 104 | 4 | 0 | L2 4, L6 15 |
| total | | | 798 | 10 | 788 | 0 | 768 | 20 | 10 | L2 20, L6 200, R1 10 |

No group has a BUILD row that is not PASS. `exit 1` means the referee reported at least one FAIL row. Every group has
L6 FAILs: the module docstring lacks a `## Main results` section.

`MainSolution.hodge_conjecture_for_cm_abelian_varieties` (group 1199): `REFEREE CLASS ... REVIEW computed class A?`.
`MainSubmission`: `REFEREE MODULE ... INFO 0 theorems checked`.

The spine (`spine_mac.py`, the statistics of `analysis/hodge-closure/spine.py`, over the closure
run with these ten groups put in) has 190 modules, none of them in a BUILD FAIL group, and 427 CLASS rows: 426 REVIEW /
computed class A? and 1 PASS / computed class DEF (`spine-2026-11-06.tsv`, `spine-class-2026-11-06.tsv`).

## Checking the files

`MANIFEST-md5.txt` lists the md5 of every file added with these results. The ten groups' 81 output files (referee,
census, unfold) were copied from the VM to a Mac in two pulls, on 5 Nov 23:07 UTC (the nine finished groups, 73 files)
and 6 Nov 04:13 UTC (group 1199, 8 files, `WATCH-1199.log`). Each pull was md5-compared file by file against the VM.
A full pull of `results-hodge/` (19,869 files) also md5-matched. The VM stopped itself at 2026-11-06 04:15:23 UTC, once
no rerun was left.

In the public copy, the `logs/hodge/` files listed in `MANIFEST-md5-2.txt` are in `logs/hodge-run/` (the same ten files, the same md5s).
