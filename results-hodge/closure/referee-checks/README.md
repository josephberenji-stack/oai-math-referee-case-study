# Checks of the referee itself, at the closure run's version

These files show that the referee used for the closure passes its own controls on this library's toolchain.

- `selftest-6e33e0d-lean4.34.1.out`: `referee_lean.py --project=<openai/math lean dir> --selftest --mutations`, with Discipline-Architecture-2 at `6e33e0d4b57af8e8f0db01dec5880bbd9a41a840`, on Lean 4.34.1 inside openai/math at `7ef5c0cc` (run on a Mac, 6 Nov 2026, 29 minutes).
  - Self-test: `85 of 85 expectations met`. L7 is off by default.
  - Mutations: each check is switched off in turn, and the self-test then fails. The last line reads "every check is needed: the self-test fails with any one of …". Exit 0.
- The step-limit patch used for the ten reruns (`../rerun-2026-11-03-hb/referee-heartbeat-fix-d83968be.patch`) changes only the limit the referee's own commands run under, not what any check decides.

## Reproduction of one group on a second machine

- `group-482.reproduced.out`: group 482 (25 modules, `../GROUPS.tsv`) refereed again from scratch on a Mac, on 6 Nov 2026. The setup was openai/math at `7ef5c0cc` with the group's 482-module closure compiled on that machine, Lean 4.34.1, DA-2 at `6e33e0d`, `REFEREE_MEM=16384`, the closure registry, and `--unfold-out`. It took 6 minutes 14 seconds.
- Compared with the closure run's `../referee/group-482.out`: **2,364 of 2,364 REFEREE rows are identical, detail text included.**
- The unfold file it wrote has the same md5 as the published `../unfold/group-482/…unfold.tsv` (`a3079af232d31d2c334960819aec1183`).
- A first attempt at the referee's default memory cap (6,144 MB) stopped with `BUILD FAIL … lean::memory_exception`. That is the failure the closure run's memory caps exist for, and it is kept in this file's history.
