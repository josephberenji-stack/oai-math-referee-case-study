#!/bin/bash
# oai-hodge-vm.sh:  the Hodge configuration and its whole import closure, built and refereed (PREREG, "The Hodge
# closure in full, with the expanded referee", 1 Nov 2026).  It reuses scripts/oai-vm.sh (sourced, nothing in it
# changed) and replaces its stages, its results folder and its branch.
#
# Instance metadata, as for oai-vm.sh (gh-token, casestudy-commit, da2-commit, comparator-timeout, skip-stages,
# stop-when-done), and:
#   referee-jobs        referee processes at once over the closure                                    (default nproc / 4)
#   group-size          closure modules per referee process                                           (default 25)
# Stages:  system, repos, tools, deps (oai-vm.sh's own);  hodgebuild (the challenge and solution modules of main.json:
# lake builds the 257 helper files and the 33,169-module closure);  hodgeside (run_all.py with --config and --helpers:
# referee, census and statement origins on the theorem, H1, H2, H4, H5 and N1-N4);  hodgecmp (real Comparator on
# main.json, H3);  closure (the referee with --unfold-out and the census on every built module of the closure, in groups;
# HC1-HC4 and the recorded rows).
# Output:  results-hodge/ and logs/hodge-run/ on the branch hodge-run.
set -u
# the base driver:  /usr/local/sbin/oai-vm.sh, written from the metadata (`oai-vm-script`) on the first boot, before it
# is sourced (Correction 1, 1 Nov 2026:  the first version sourced it from the startup script's temporary folder, where
# it does not exist, and the boot stopped at "CS: unbound variable")
OAI_VM_LIB=${OAI_VM_LIB:-/usr/local/sbin/oai-vm.sh}
if [ ! -s "$OAI_VM_LIB" ]; then
  curl -sf -H 'Metadata-Flavor: Google' \
    http://metadata.google.internal/computeMetadata/v1/instance/attributes/oai-vm-script > "$OAI_VM_LIB.new" &&
    [ -s "$OAI_VM_LIB.new" ] && chmod 0755 "$OAI_VM_LIB.new" && mv -f "$OAI_VM_LIB.new" "$OAI_VM_LIB" ||
    { echo "oai-hodge: no base driver (metadata oai-vm-script)" > /dev/console; exit 1; }
fi
export OAI_VM_SOURCE_ONLY=1
# shellcheck source=oai-vm.sh
. "$OAI_VM_LIB"
unset OAI_VM_SOURCE_ONLY

BRANCH=hodge-run
RES=$CS/results-hodge
LOGS=$TOP/logs-hodge
STATE=/var/lib/oai-hodge
SELF=/usr/local/sbin/oai-hodge-vm.sh
CFG=ComparatorChallenges/HodgeConjectureCMAbelianVarieties/main.json
STAGES=(system repos tools deps hodgebuild hodgeside hodgecmp closure)
OVL=/srv/oai/closure-root   # Correction 5:  the overlay project root of the closure groups

publish() {          # publish MESSAGE:  results-hodge/ and logs/hodge-run/ on the branch hodge-run
  [ -d "$CS/.git" ] || return 0
  (
    flock 9
    mkdir -p "$RES" "$CS/logs/hodge-run"
    cp /var/log/oai-hodge.log "$LOGS/oai-hodge.log" 2>/dev/null
    for f in "$LOGS"/*; do
      [ -f "$f" ] || continue
      b=${f##*/}
      if [ "$(stat -c %s "$f")" -gt 40000000 ]; then gzip -c "$f" > "$CS/logs/hodge-run/$b.gz"; rm -f "$CS/logs/hodge-run/$b"
      else cp "$f" "$CS/logs/hodge-run/$b"; rm -f "$CS/logs/hodge-run/$b.gz"; fi
    done
    find "$RES" "$CS/logs/hodge-run" -type f -size +95M -printf '%p\t%s\n' > "$STATE/big.tsv"
    while IFS="$TAB" read -r f size; do
      rel=${f#"$CS"/}
      grep -qxF "/$rel" "$CS/.git/info/exclude" 2>/dev/null || echo "/$rel" >> "$CS/.git/info/exclude"
      GCS rm -q --cached --ignore-unmatch -- "$rel" >/dev/null 2>&1
      printf '%s\t%s\n' "$rel" "$size"
    done < "$STATE/big.tsv" > "$STATE/big-rel.tsv"
    [ -s "$STATE/big-rel.tsv" ] && cp "$STATE/big-rel.tsv" "$RES/NOT-IN-GIT.tsv"
    GCS add -A -- results-hodge logs/hodge-run
    GCS diff --cached --quiet || GCS commit -q -m "$1"
    GCS push -q origin "HEAD:$BRANCH" || say "push failed;  the next publish retries"
  ) 9> "$STATE/publish.lock"
}

# stage deps (oai-vm.sh's) writes into $RES:  make it after the clone exists, then run the original
eval "base_$(declare -f stage_deps)"
stage_deps() { mkdir -p "$RES" && chown "$LUSER:$LUSER" "$RES" && base_stage_deps; }

stage_hodgebuild() {
  needs deps > "$STATE/hodgebuild.why" || return 3
  mkdir -p "$RES" && chown "$LUSER:$LUSER" "$RES"
  local chal sol
  chal=$(jq -r .challenge_module "$LEANDIR/$CFG"); sol=$(jq -r .solution_module "$LEANDIR/$CFG")
  build_target "hodge" "$chal" "$sol"
}

stage_hodgeside() {
  needs hodgebuild > "$STATE/hodgeside.why" || return 3
  local ram mem; ram=$(awk '/MemTotal/{print int($2/1024)}' /proc/meminfo); mem=$(( ram * 3 / 4 ))
  [ "$mem" -gt 65536 ] && mem=65536
  mkdir -p "$RES" && chown "$LUSER:$LUSER" "$RES"
  asl bash -c 'cd "$1" && python3 -I scripts/run_all.py sources/openai-math/lean ../da2/discipline/lean "$2" \
                 --side=solution --mem="$3" --config="$4" --helpers=HodgeConjecture' _ "$CS" "$RES" "$mem" "$CFG"
}

stage_hodgecmp() {
  needs tools deps hodgebuild > "$STATE/hodgecmp.why" || return 3
  cmp_ready > "$STATE/hodgecmp.why" || return 3
  mkdir -p "$RES/comparator" && chown "$LUSER:$LUSER" "$RES/comparator"
  [ -s "$RES/comparator/summary.tsv" ] || printf 'challenge\texit\tseconds\toutcome\tlast_line\n' > "$RES/comparator/summary.tsv"
  grep -q "^HodgeConjectureCMAbelianVarieties$TAB" "$RES/comparator/summary.tsv" && return 0
  one_comparator "$LEANDIR" "$CFG" "$RES/comparator/HodgeConjectureCMAbelianVarieties" \
    HodgeConjectureCMAbelianVarieties "$RES/comparator/summary.tsv" "$(setting comparator-timeout 10800)"
}

stage_closure() {    # every module the build compiled (only the Hodge targets were built on this disk), in groups
  needs hodgebuild > "$STATE/closure.why" || return 3
  local out="$RES/closure" lib="$LEANDIR/.lake/build/lib/lean" j g ram mem
  j=$(setting referee-jobs $(( $(nproc) / 4 ))); g=$(setting group-size 25)
  ram=$(awk '/MemTotal/{print int($2/1024)}' /proc/meminfo); mem=$(( ram * 3 / 4 / j )); [ "$mem" -gt 32768 ] && mem=32768
  mkdir -p "$out/referee" "$out/census" "$out/unfold" && chown -R "$LUSER:$LUSER" "$out"
  # Correction 5 (found by this thread, 1 Nov 2026, 14:50 UTC):  the first closure pass ran in 56 s and every one of its
  # 2,181 groups stopped on a harness error, not a referee verdict:  `lake` was not on PATH (the group re-sources the
  # base script, which resets PATH), and the HodgeConjecture modules live under the lakefile's srcDir
  # ComparatorChallenges/HodgeConjectureCMAbelianVarieties, not at the root, so their sources were not found.  The
  # groups' "exit 1" lines counted them as done.  Now:  the groups run in an overlay root ($OVL) whose OAI and
  # HodgeConjecture entries point at the two source roots and whose lakefile, manifest, toolchain and .lake are the
  # build's own (symlinks;  nothing in openai/math is written, and the referee's temporary files land in the overlay);
  # PATH is set in the group;  a group whose output holds a Python traceback is a harness error, moved aside and rerun.
  G -C "$DA2" fetch -q origin && G -C "$DA2" checkout -q --detach "$(setting da2-commit)" || return 1   # Correction 6
  mkdir -p "$OVL" && for x in lakefile.lean lake-manifest.json lean-toolchain .lake OAI ComparatorChallenges; do
    ln -sfn "$LEANDIR/$x" "$OVL/$x"; done
  ln -sfn "$LEANDIR/ComparatorChallenges/HodgeConjectureCMAbelianVarieties/HodgeConjecture" "$OVL/HodgeConjecture"
  chown -h -R "$LUSER:$LUSER" "$OVL"
  for f in "$out"/referee/group-*.out; do
    [ -e "$f" ] && grep -q '^Traceback' "$f" && mv -f "$f" "$f.harness-error"
  done
  # the registry:  the closure's roots (Correction 3, 1 Nov 2026:  without it the referee reads Discipline-Architecture-2's
  # own registry, which names no root, and treats every OAI module as outside library;  run_all.py passes
  # referee/registry.tsv, the closure pass must pass its own)
  { grep -v '^root' "$CS/referee/registry.tsv"; printf 'root\tOAI\nroot\tHodgeConjecture\nroot\tHodgeCM\n'; } > "$out/registry.tsv"
  chown "$LUSER:$LUSER" "$out/registry.tsv"
  ( cd "$lib" && find OAI HodgeConjecture -name '*.olean' 2>/dev/null | sed 's|\.olean$||; s|/|.|g' | sort ) > "$out/MODULES.txt"
  echo "closure modules with an olean: $(wc -l < "$out/MODULES.txt")"
  # groups of g modules from one folder:  sort keeps a folder's modules together
  awk -v g="$g" '{ f=$0; sub(/\.[^.]*$/, "", f); if (f != pf || n == g) { k++; n = 0 }; pf = f; n++; print k "\t" $0 }' \
    "$out/MODULES.txt" > "$out/GROUPS.tsv"
  cut -f1 "$out/GROUPS.tsv" | uniq | while read -r k; do
    grep -q '^exit ' "$out/referee/group-$k.out" 2>/dev/null || echo "$k"
  done | asl env REFEREE_MEM="$mem" xargs -r -P "$j" -n 1 "$SELF" group
  # every group is in the denominator:  one with no exit line is listed and the stage is not done
  # Correction 6 (found by this thread, 1 Nov 2026, 15:05 UTC):  a group that stopped on a Python traceback has an exit
  # line but no verdict;  it is counted as missing, so the stage is not done.  And the referee is checked out at the
  # metadata's da2-commit at the start of the stage, so a referee fix reaches a rerun without redoing stage repos.
  cut -f1 "$out/GROUPS.tsv" | uniq | while read -r k; do
    f="$out/referee/group-$k.out"; { grep -q '^exit ' "$f" && ! grep -q '^Traceback' "$f"; } 2>/dev/null || echo "$k"
  done > "$out/MISSING.txt"
  [ -s "$out/MISSING.txt" ] && { echo "groups with no exit line or a traceback: $(wc -l < "$out/MISSING.txt")"; return 1; }
  rm -f "$out/MISSING.txt"
}

boot() {
  mkdir -p "$STATE"
  { meta attributes/startup-script > "$SELF.new" && [ -s "$SELF.new" ]; } || cp "$0" "$SELF.new"
  chmod 0755 "$SELF.new" && mv -f "$SELF.new" "$SELF"
  sysctl -q -w vm.max_map_count=262144
  guard_metadata
  # Correction 4 (found by this thread, 1 Nov 2026, 14:39 UTC):  a stage skipped by skip-stages counted as done, so
  # ALL.done was set after the closure was skipped;  the restart for the closure then found ALL.done, did nothing and
  # never stopped (64 CPUs idle 11:17-14:40 UTC).  A finished run now also stops the machine, and a stage named in
  # skip-stages is not counted as done once skip-stages no longer names it.
  # Correction 5:  redo-stages (comma-separated) reopens stages whose .done was set by a pass that did not do them
  for s in $(setting redo-stages "" | tr ',' ' '); do
    [ -e "$STATE/$s.done" ] && { mv -f "$STATE/$s.done" "$STATE/$s.done.prev"; [ -e "$STATE/ALL.done" ] && mv -f "$STATE/ALL.done" "$STATE/ALL.done.prev"; }
  done
  if [ -e "$STATE/ALL.done" ]; then
    for s in "${STAGES[@]}"; do
      [ -e "$STATE/$s.skipped" ] && ! setting skip-stages "" | tr ', ' '\n\n' | grep -qx "$s" \
        && { mv -f "$STATE/$s.skipped" "$STATE/$s.skipped.prev"; mv -f "$STATE/ALL.done" "$STATE/ALL.done.prev"; }
    done
  fi
  if [ -e "$STATE/ALL.done" ]; then
    say "the run is finished;  nothing to do"
    [ "$(setting stop-when-done yes)" = yes ] && { say "stopping the machine"; shutdown -h +1; }
    exit 0
  fi
  systemctl is-active -q oai-hodge && exit 0
  systemctl reset-failed oai-hodge 2>/dev/null
  systemd-run --unit=oai-hodge -p LimitNOFILE=1048576 -p StandardOutput=append:/var/log/oai-hodge.log \
    -p StandardError=append:/var/log/oai-hodge.log "$SELF" work
}

work() {
  exec 8> "$STATE/work.lock"; flock -n 8 || { say "another run holds the lock"; exit 0; }
  mkdir -p "$LOGS"     # not $RES:  it lies inside the case study's clone, which stage repos creates (Correction 2,
  say "work: start"    # 1 Nov 2026:  an early mkdir made the folder and the clone refused it)
  ( while sleep 1800; do publish "hodge run: progress $(ts)"; done ) &
  local pub=$! s all=1
  for s in "${STAGES[@]}"; do run_stage "$s"; done
  kill "$pub" 2>/dev/null
  for s in "${STAGES[@]}"; do [ -e "$STATE/$s.done" ] || [ -e "$STATE/$s.skipped" ] || all=0; done
  echo "- this boot's pass ended: $(ts);  every stage done: $([ $all = 1 ] && echo yes || echo no)" >> "$LOGS/RUN-INFO.md"
  publish "hodge run: $([ $all = 1 ] && echo 'every stage done' || echo 'pass ended, stages not done (logs/hodge-run/STAGES.tsv)')"
  [ $all = 1 ] && touch "$STATE/ALL.done"
  if [ "$(setting stop-when-done yes)" = yes ]; then say "stopping the machine"; shutdown -h +1; fi
}

group() {           # group K:  the referee (with its unfold pass) and the census on closure group K, as the Lean user
  local out="$RES/closure" k=$1 m
  m=$(awk -F'\t' -v k="$k" '$1 == k { print $2 }' "$out/GROUPS.tsv" | paste -sd, -)
  export DISCIPLINE_LEAN_REGISTRY="$out/registry.tsv"
  export PATH="$LPATH"   # Correction 5
  cd "$OVL" || return 1
  python3 -I "$DA2/discipline/lean/referee_lean.py" --project=. --modules="$m" --unfold-out="$out/unfold/group-$k" \
    > "$out/referee/group-$k.out" 2>&1
  echo "exit $?" >> "$out/referee/group-$k.out"
  python3 -I "$DA2/discipline/lean/census/census.py" --project=. --modules="$m" --out="$out/census/group-$k" \
    --referee-log="$out/referee/group-$k.out" > "$out/census/group-$k.out" 2>&1
  echo "exit $?" >> "$out/census/group-$k.out"
}

case "${1:-boot}" in
  boot)  boot ;;
  work)  work ;;
  group) group "$2" ;;
  *)    echo "usage: $0 [boot | work | group K]"; exit 2 ;;
esac
