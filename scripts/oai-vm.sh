#!/bin/bash
# oai-vm.sh  --  CLOUD-PLAN.md's full run on one Google Cloud VM (Ubuntu 24.04), given to the VM as its startup script.
#
# At every boot it runs as root, re-applies two machine settings, starts itself as the systemd service `oai-run`, and
# exits.  The service runs the stages below in order.  A stage that completes leaves a marker in /var/lib/oai, so a
# machine that is stopped or rebooted resumes at the stage it was in.  A stage whose own machinery fails (a clone, a
# download) is recorded as FAILED in logs/full-run/STAGES.tsv and is tried again at the next boot;  a challenge that does
# not build, is not refereed, or is not accepted by Comparator is a result:  it is recorded and never rerun.
#
# After every stage, and every 30 minutes inside one, results-full/ and logs/full-run/ are committed to
# lean-referee-case-study on the branch `full-run` and pushed.  When the last stage ends the machine stops itself.
#
# Instance metadata (gcloud compute instances create ... --metadata=KEY=VALUE,...):
#   gh-token            GitHub token:  Contents read/write on lean-referee-case-study, read on Discipline-Architecture-2.
#                       Root reads it only to clone and to push;  the user that runs Lean cannot reach the metadata server.
#   casestudy-commit    the commit of lean-referee-case-study to run                                       (required)
#   da2-commit          the commit of Discipline-Architecture-2 to run                                     (required)
#   runall-jobs         copies of scripts/run_all.py at once, on disjoint lists                            (default 1)
#   build-scope         challenges:  the solution modules of the 418 configs (default);  library:  lake build OAI
#   comparator-timeout  seconds allowed to one Comparator run                                              (default 10800)
#   skip-stages         stages not to run, comma-separated                                                 (default none)
#   stop-when-done      yes (default) | no
#
# Stages:  system, repos, tools, deps, bench (F6:  real Comparator on the planted-fault benchmark), chalbuild and
# chalside (the challenge files, CLOUD-PLAN 1a), solbuild and solside (the solution modules, sections 4 and 6),
# comparator (real Comparator on every config, section 5).
set -u
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/go/bin
export LANG=C.UTF-8 LC_ALL=C.UTF-8

OPENAI_URL=https://github.com/openai/math.git
OPENAI_COMMIT=7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a
CASESTUDY_URL=https://github.com/josephberenji-stack/lean-referee-case-study.git
DA2_URL=https://github.com/josephberenji-stack/Discipline-Architecture-2.git
COMPARATOR_URL=https://github.com/leanprover/comparator.git
COMPARATOR_COMMIT=d03acab154d269c06e60e4de7e4cc85deebff94b  # toolchain v4.34.0;  every later commit changes only the
                                                            # toolchain, the nanoda tests' folder and the README
LANDRUN_URL=https://github.com/Zouuup/landrun.git
LANDRUN_COMMIT=ec104f6edc1e14d7fec6d31146f1ec6f9c192c5a     # main on 16 Oct 2026 (Comparator's README:  built from main)
LEAN_TOOLCHAIN=leanprover/lean4:v4.34.1                       # openai/math's lean/lean-toolchain;  lean4export must match it
BRANCH=full-run
GIT_NAME="Joseph Berenji"
GIT_EMAIL="327663643+josephberenji-stack@users.noreply.github.com"

TOP=/srv/oai
CS=$TOP/casestudy
DA2=$TOP/da2
OAI=$CS/sources/openai-math
LEANDIR=$OAI/lean
TOOLS=$TOP/tools
BENCH=$TOP/bench
LOGS=$TOP/logs
RES=$CS/results-full
STATE=/var/lib/oai
SELF=/usr/local/sbin/oai-vm.sh
CRED=/usr/local/sbin/oai-git-cred
LUSER=lean
LHOME=/home/$LUSER
LPATH=$LHOME/.elan/bin:$TOOLS/bin:/usr/local/go/bin:/usr/local/bin:/usr/bin:/bin
STAGES=(system repos tools deps bench chalbuild chalside solbuild solside comparator)
TAB=$'\t'

ts()      { date -u +%Y-%m-%dT%H:%M:%SZ; }
say()     { echo "$(ts) $*"; }
meta()    { curl -sf -H 'Metadata-Flavor: Google' "http://metadata.google.internal/computeMetadata/v1/instance/$1"; }
setting() { local v; v=$(meta "attributes/$1" 2>/dev/null) && [ -n "$v" ] && { printf '%s\n' "$v"; return 0; }
            printf '%s\n' "${2-}"; }
asl()     { sudo -u "$LUSER" -H env -i HOME="$LHOME" USER="$LUSER" LANG=C.UTF-8 LC_ALL=C.UTF-8 PATH="$LPATH" "$@"; }
G()       { git -c safe.directory='*' -c credential.helper= -c credential.helper="$CRED" "$@"; }
GCS()     { G -C "$CS" -c user.name="$GIT_NAME" -c user.email="$GIT_EMAIL" "$@"; }
names()   { ls "$LEANDIR/ComparatorChallenges" | sed -n 's/\.json$//p' | sort; }

guard_metadata() {   # the user that runs Lean cannot reach the metadata server, where the token is
  local u; u=$(id -u "$LUSER" 2>/dev/null) || return 0
  iptables -C OUTPUT -d 169.254.169.254 -m owner --uid-owner "$u" -j REJECT 2>/dev/null ||
    iptables -I OUTPUT -d 169.254.169.254 -m owner --uid-owner "$u" -j REJECT
}

write_cred() {       # git credential helper for root:  the token, read from the metadata at the moment git asks
  cat > "$CRED" <<'EOF'
#!/bin/sh
[ "$1" = get ] || exit 0
t=$(curl -sf -H 'Metadata-Flavor: Google' http://metadata.google.internal/computeMetadata/v1/instance/attributes/gh-token) || exit 0
printf 'username=x-access-token\npassword=%s\n' "$t"
EOF
  chmod 700 "$CRED"
}

# --- publishing:  results-full/ and logs/full-run/ on the run's branch -------------------------------------------------
publish() {          # publish MESSAGE
  [ -d "$CS/.git" ] || return 0
  (
    flock 9
    mkdir -p "$RES" "$CS/logs/full-run"
    cp /var/log/oai-run.log "$LOGS/oai-run.log" 2>/dev/null
    for f in "$LOGS"/*; do
      [ -f "$f" ] || continue
      b=${f##*/}
      if [ "$(stat -c %s "$f")" -gt 40000000 ]; then
        gzip -c "$f" > "$CS/logs/full-run/$b.gz"; rm -f "$CS/logs/full-run/$b"
      else
        cp "$f" "$CS/logs/full-run/$b"; rm -f "$CS/logs/full-run/$b.gz"
      fi
    done
    # a file GitHub would refuse (over 95 MB) stays on the disk and is listed in results-full/NOT-IN-GIT.tsv
    find "$RES" "$CS/logs/full-run" -type f -size +95M -printf '%p\t%s\n' > "$STATE/big.tsv"
    while IFS="$TAB" read -r f size; do
      rel=${f#"$CS"/}
      grep -qxF "/$rel" "$CS/.git/info/exclude" 2>/dev/null || echo "/$rel" >> "$CS/.git/info/exclude"
      GCS rm -q --cached --ignore-unmatch -- "$rel" >/dev/null 2>&1
      printf '%s\t%s\n' "$rel" "$size"
    done < "$STATE/big.tsv" > "$STATE/big-rel.tsv"
    [ -s "$STATE/big-rel.tsv" ] && cp "$STATE/big-rel.tsv" "$RES/NOT-IN-GIT.tsv"
    GCS add -A -- results-full logs/full-run
    GCS diff --cached --quiet || GCS commit -q -m "$1"
    GCS push -q origin "$BRANCH" || say "push failed;  the next publish retries"
  ) 9> "$STATE/publish.lock"
}

# --- stage bookkeeping -------------------------------------------------------------------------------------------------
record_stage() {     # record_stage NAME START STATUS
  [ -s "$LOGS/STAGES.tsv" ] || printf 'stage\tstart\tend\tstatus\n' > "$LOGS/STAGES.tsv"
  printf '%s\t%s\t%s\t%s\n' "$1" "$2" "$(ts)" "$3" >> "$LOGS/STAGES.tsv"
  # also on the serial console (gcloud compute instances get-serial-port-output), readable even if a push fails
  echo "oai-run $(ts) stage $1: $3" > /dev/console 2>/dev/null || true
}

needs() {            # needs STAGE...:  prints the first stage not done
  local s; for s in "$@"; do [ -e "$STATE/$s.done" ] || { echo "needs stage $s"; return 1; }; done
}

run_stage() {        # run_stage NAME:  0 = done (marker), 3 = not run (its reason in $STATE/NAME.why), other = FAILED
  local n=$1 t0 rc
  [ -e "$STATE/$n.done" ] || [ -e "$STATE/$n.skipped" ] && return 0
  if [[ ",$(setting skip-stages)," == *",$n,"* ]]; then
    touch "$STATE/$n.skipped"; record_stage "$n" "$(ts)" "skipped (skip-stages)"; return 0
  fi
  t0=$(ts); say "stage $n: start"
  "stage_$n" >> "$LOGS/stage-$n.log" 2>&1; rc=$?
  case $rc in
    0) touch "$STATE/$n.done"; record_stage "$n" "$t0" "done" ;;
    3) record_stage "$n" "$t0" "not run:  $(cat "$STATE/$n.why" 2>/dev/null)" ;;
    *) record_stage "$n" "$t0" "FAILED (exit $rc;  logs/full-run/stage-$n.log)" ;;
  esac
  say "stage $n: exit $rc"
  publish "full run: stage $n, $(tail -1 "$LOGS/STAGES.tsv" | cut -f4)"
}

# --- Comparator, as its README runs it (README.md:49:  systemd-run --user, AF_UNIX restricted), unattended -------------
cmp_exec() {         # cmp_exec DIR SECONDS CMD...:  as the Lean user, with Comparator's tools, under the time limit
  local dir=$1 tmo=$2 luid; shift 2; luid=$(id -u "$LUSER")
  if [ "$(cat "$STATE/cmp-mode" 2>/dev/null)" = direct ]; then
    asl env COMPARATOR_LANDRUN="$TOOLS/bin/landrun" COMPARATOR_LEAN4EXPORT="$TOOLS/bin/lean4export" \
      bash -c 'cd "$1" && shift && exec /usr/bin/timeout -k 120 "$@"' _ "$dir" "$tmo" "$@"
  else
    asl env XDG_RUNTIME_DIR="/run/user/$luid" DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$luid/bus" \
      systemd-run --user --wait --pipe --collect --quiet --property=RestrictAddressFamilies=~AF_UNIX \
        -E PATH="$LPATH" -E HOME="$LHOME" -E LANG=C.UTF-8 \
        -E COMPARATOR_LANDRUN="$TOOLS/bin/landrun" -E COMPARATOR_LEAN4EXPORT="$TOOLS/bin/lean4export" \
        --working-directory="$dir" -- /usr/bin/timeout -k 120 "$tmo" "$@"
  fi
}

cmp_ready() {        # Comparator's own tests passed here, and its wrapper starts a process this boot (else no verdict
                     # is taken:  a wrapper that cannot start would read as a rejection)
  [ -e "$STATE/selftest.ok" ] ||
    { echo "Comparator's own tests did not pass here (results-full/tools/comparator-selftest.out)"; return 1; }
  local try; for try in 1 2 3 4 5 6; do
    cmp_exec "$TOOLS" 60 /bin/true >/dev/null 2>&1 && return 0
    [ "$try" = 6 ] || sleep 20
  done
  echo "Comparator's wrapper ($(cat "$STATE/cmp-mode" 2>/dev/null)) could not start a process this boot"; return 1
}

one_comparator() {   # one_comparator DIR CONFIG OUTBASE NAME SUMMARY SECONDS:  OUTBASE.out and one row of SUMMARY
  local dir=$1 cfg=$2 ob=$3 name=$4 sum=$5 tmo=$6 t0 rc secs outcome last
  t0=$(date +%s)
  cmp_exec "$dir" "$tmo" lake env comparator "$cfg" > "$ob.out.partial" 2>&1; rc=$?
  secs=$(( $(date +%s) - t0 ))
  if [ "$rc" = 0 ] && grep -q 'Your solution is okay!' "$ob.out.partial"; then outcome=accepted
  elif { [ "$rc" = 124 ] || [ "$rc" = 137 ]; } && [ "$secs" -ge "$tmo" ]; then outcome="timeout ($tmo s)"
  elif [ "$rc" = 137 ]; then outcome="killed (signal 9, before the time limit)"
  else outcome="not accepted"; fi
  last=$(grep -v '^[[:space:]]*$' "$ob.out.partial" | tail -1 | tr '\t' ' ' | cut -c1-300)
  mv -f "$ob.out.partial" "$ob.out"
  ( flock 9; printf '%s\t%s\t%s\t%s\t%s\n' "$name" "$rc" "$secs" "$outcome" "$last" >> "$sum" ) 9> "$STATE/summary.lock"
}

# --- the stages ----------------------------------------------------------------------------------------------------------
stage_system() {
  export DEBIAN_FRONTEND=noninteractive
  apt-get -o DPkg::Lock::Timeout=900 update -q || return 1
  apt-get -o DPkg::Lock::Timeout=900 install -y -q git curl jq python3 iptables build-essential ca-certificates || return 1
  id -u "$LUSER" >/dev/null 2>&1 || useradd -m -s /bin/bash "$LUSER" || return 1
  guard_metadata || return 1
  loginctl enable-linger "$LUSER" || return 1
  systemctl start "user@$(id -u "$LUSER").service" || return 1
  printf 'vm.max_map_count=262144\n' > /etc/sysctl.d/90-oai.conf && sysctl -q -p /etc/sysctl.d/90-oai.conf || return 1
  if ! swapon --show=NAME --noheadings | grep -qx /swapfile; then   # slows a memory peak instead of killing a build job
    [ -e /swapfile ] || { fallocate -l 32G /swapfile && chmod 600 /swapfile && mkswap -q /swapfile; } || return 1
    swapon /swapfile || return 1
    grep -q '^/swapfile ' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
  fi
  if [ ! -x /usr/local/go/bin/go ]; then
    local v; v=$(curl -sSfL 'https://go.dev/VERSION?m=text' | head -1) || return 1
    curl -sSfL "https://go.dev/dl/$v.linux-amd64.tar.gz" | tar -C /usr/local -xz || return 1
  fi
  mkdir -p "$TOOLS/bin" "$BENCH" && chown -R "$LUSER:$LUSER" "$TOP" || return 1
  write_cred
  {
    echo "# Full run:  the machine and the inputs"
    echo
    echo "- first boot of the run: $(ts)"
    echo "- machine type: $(meta machine-type | sed 's#.*/##');  zone: $(meta zone | sed 's#.*/##')"
    echo "- CPUs: $(nproc);  memory: $(free -g | awk '/^Mem:/{print $2}') GB;  disk: $(df -h / | awk 'NR==2{print $2}')"
    echo "- image: $(. /etc/os-release; echo "$PRETTY_NAME");  kernel: $(uname -r)"
    echo "- kernel security modules: $(cat /sys/kernel/security/lsm 2>/dev/null)"
  } > "$LOGS/RUN-INFO.md"
}

stage_repos() {
  needs system > "$STATE/repos.why" || return 3
  local csc dac
  csc=$(setting casestudy-commit); dac=$(setting da2-commit)
  [ -n "$csc" ] && [ -n "$dac" ] || { echo "casestudy-commit and da2-commit must be set in the metadata"; return 1; }
  [ -d "$CS/.git" ] || G clone -q "$CASESTUDY_URL" "$CS" || return 1
  G -C "$CS" fetch -q origin || return 1
  if G -C "$CS" rev-parse -q --verify "refs/remotes/origin/$BRANCH" >/dev/null; then
    G -C "$CS" checkout -q -B "$BRANCH" "origin/$BRANCH" || return 1
  else
    G -C "$CS" checkout -q -B "$BRANCH" "$csc" || return 1
  fi
  G -C "$CS" merge-base --is-ancestor "$csc" HEAD || { echo "branch $BRANCH does not contain $csc"; return 1; }
  [ -d "$DA2/.git" ] || G clone -q "$DA2_URL" "$DA2" || return 1
  G -C "$DA2" fetch -q origin && G -C "$DA2" checkout -q --detach "$dac" || return 1
  mkdir -p "$OAI"
  [ -d "$OAI/.git" ] || { G -C "$OAI" init -q && G -C "$OAI" remote add origin "$OPENAI_URL"; } || return 1
  if [ "$(G -C "$OAI" rev-parse -q --verify HEAD 2>/dev/null)" != "$OPENAI_COMMIT" ]; then
    G -C "$OAI" fetch -q --depth 1 origin "$OPENAI_COMMIT" && G -C "$OAI" checkout -q --detach "$OPENAI_COMMIT" || return 1
  fi
  chown -R "$LUSER:$LUSER" "$TOP" || return 1
  {
    echo "- lean-referee-case-study: $(G -C "$CS" rev-parse "$csc") (results on the branch $BRANCH)"
    echo "- Discipline-Architecture-2: $(G -C "$DA2" rev-parse HEAD)"
    echo "- openai/math: $(G -C "$OAI" rev-parse HEAD)"
    echo "- settings: runall-jobs=$(setting runall-jobs 1)  build-scope=$(setting build-scope challenges)" \
         " comparator-timeout=$(setting comparator-timeout 10800)  stop-when-done=$(setting stop-when-done yes)"
  } >> "$LOGS/RUN-INFO.md"
}

stage_tools() {
  needs system > "$STATE/tools.why" || return 3
  if [ ! -x "$LHOME/.elan/bin/elan" ]; then
    asl bash -c 'curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh |
                 sh -s -- -y --default-toolchain none --no-modify-path' || return 1
  fi
  asl elan toolchain install "$LEAN_TOOLCHAIN" || return 1
  [ -d "$TOOLS/landrun/.git" ] || asl git clone -q "$LANDRUN_URL" "$TOOLS/landrun" || return 1
  asl git -C "$TOOLS/landrun" checkout -q --detach "$LANDRUN_COMMIT" || return 1
  asl bash -c 'cd "$1" && GOTOOLCHAIN=local go build -o "$2" cmd/landrun/main.go' _ "$TOOLS/landrun" "$TOOLS/bin/landrun" ||
    return 1
  [ -d "$TOOLS/comparator/.git" ] || asl git clone -q "$COMPARATOR_URL" "$TOOLS/comparator" || return 1
  asl git -C "$TOOLS/comparator" checkout -q --detach "$COMPARATOR_COMMIT" || return 1
  asl bash -c 'cd "$1" && printf "%s\n" "$2" > lean-toolchain && lake build lean4export comparator' \
    _ "$TOOLS/comparator" "$LEAN_TOOLCHAIN" || return 1
  ln -sf "$TOOLS/comparator/.lake/build/bin/comparator" "$TOOLS/bin/comparator"
  ln -sf "$TOOLS/comparator/.lake/packages/lean4export/.lake/build/bin/lean4export" "$TOOLS/bin/lean4export"
  rm -f "$STATE/cmp-mode"
  if cmp_exec "$TOOLS" 120 /bin/true; then echo systemd-run > "$STATE/cmp-mode"; else echo direct > "$STATE/cmp-mode"; fi
  # the control:  Comparator's own tests (all but the nanoda ones, which need a second kernel not installed here),
  # each with an expected exit code, accepting and rejecting cases both;  the Comparator stages run only if they pass
  mkdir -p "$RES/tools"
  local rc tests
  tests=$(for d in "$TOOLS/comparator/tests/projects"/*/; do d=${d%/}; d=${d##*/}; [[ $d == *nanoda* ]] || echo "$d"; done)
  # shellcheck disable=SC2086
  cmp_exec "$TOOLS/comparator" 3600 lean --run runtests.lean $tests > "$RES/tools/comparator-selftest.out" 2>&1; rc=$?
  echo "exit $rc" >> "$RES/tools/comparator-selftest.out"
  if [ "$rc" = 0 ]; then touch "$STATE/selftest.ok"; else rm -f "$STATE/selftest.ok"; fi
  {
    echo "- Lean: $LEAN_TOOLCHAIN;  $(asl elan --version)"
    echo "- Comparator: $COMPARATOR_COMMIT, built with $LEAN_TOOLCHAIN;  lean4export:" \
         "$(G -C "$TOOLS/comparator/.lake/packages/lean4export" rev-parse HEAD)"
    echo "- landrun: $LANDRUN_COMMIT;  $(go version)"
    echo "- Comparator invoked through: $(cat "$STATE/cmp-mode")"
    echo "- Comparator's own tests on this machine: exit $rc (results-full/tools/comparator-selftest.out)"
  } >> "$LOGS/RUN-INFO.md"
}

stage_deps() {
  needs repos tools > "$STATE/deps.why" || return 3
  local tc; tc=$(cat "$LEANDIR/lean-toolchain")
  [ "$tc" = "$LEAN_TOOLCHAIN" ] || { echo "openai/math's toolchain is $tc;  the tools are built for $LEAN_TOOLCHAIN"; return 1; }
  # openai/math's own steps (lean/ComparatorChallenges/README.md:7-8):  `lake update`, then `lake exe cache get`.  Its
  # lakefile patches 11 dependencies while it is elaborated and 12 more in its post_update hook (lakefile.lean:306),
  # which only `lake update` runs.  Every dependency is pinned to a commit there;  any change it makes to a tracked
  # file is recorded below.
  asl bash -c 'cd "$1" && lake update' _ "$LEANDIR" > "$LOGS/lake-update.log" 2>&1 || return 1
  G -C "$OAI" status --porcelain --untracked-files=no > "$RES/openai-tracked-changes-after-update.txt"
  G -C "$OAI" diff > "$RES/openai-diff-after-update.txt"
  asl bash -c 'cd "$1" && lake exe cache get' _ "$LEANDIR" > "$LOGS/cache-get.log" 2>&1 || return 1
  echo "- openai/math after lake update: $(wc -l < "$RES/openai-tracked-changes-after-update.txt") tracked files" \
       "changed (results-full/openai-tracked-changes-after-update.txt)" >> "$LOGS/RUN-INFO.md"
}

stage_bench() {      # F6:  real Comparator on the planted-fault benchmark, one config per theorem (CLOUD-PLAN 7)
  needs repos tools deps > "$STATE/bench.why" || return 3
  cmp_ready > "$STATE/bench.why" || return 3
  local out="$RES/benchmark-comparator" mlrev t
  mlrev=$(jq -r '.packages[] | select(.name == "mathlib") | .rev' "$LEANDIR/lake-manifest.json")
  [ -n "$mlrev" ] && [ "$mlrev" != null ] || { echo "no mathlib revision in openai/math's lake-manifest.json"; return 1; }
  mkdir -p "$BENCH/Bench" "$out/files"
  cp "$CS/benchmark/Defs.lean" "$CS/benchmark/Challenge.lean" "$BENCH/Bench/" || return 1
  # Comparator looks each name of theorem_names up in both modules (its Main.lean:305-314;  README.md:30-32), so the
  # solution declares Bench.fa ... Bench.fe:  benchmark/Solution.lean with its two namespace lines renamed, nothing else.
  sed -e 's/^namespace BenchS$/namespace Bench/' -e 's/^end BenchS$/end Bench/' "$CS/benchmark/Solution.lean" \
    > "$BENCH/Bench/Solution.lean" || return 1
  [ "$(diff "$CS/benchmark/Solution.lean" "$BENCH/Bench/Solution.lean" | grep -c '^>')" = 2 ] ||
    { echo "the namespace rename did not change exactly two lines"; return 1; }
  printf '%s\n' "$LEAN_TOOLCHAIN" > "$BENCH/lean-toolchain"
  cat > "$BENCH/lakefile.toml" <<EOF
name = "bench"
defaultTargets = ["Bench"]

[[require]]
name = "mathlib"
git = "https://github.com/leanprover-community/mathlib4.git"
rev = "$mlrev"

[[lean_lib]]
name = "Bench"
globs = ["Bench.+"]
EOF
  for t in fa fb fc fd fe; do
    printf '{"challenge_module": "Bench.Challenge", "solution_module": "Bench.Solution", "theorem_names": ["Bench.%s"], "permitted_axioms": ["propext", "Quot.sound", "Classical.choice"]}\n' \
      "$t" > "$BENCH/config-$t.json"
  done
  chown -R "$LUSER:$LUSER" "$BENCH" || return 1
  asl bash -c 'cd "$1" && lake exe cache get && lake build Bench.Defs' _ "$BENCH" > "$LOGS/bench-setup.log" 2>&1 || return 1
  cp "$BENCH/Bench/"*.lean "$BENCH/lakefile.toml" "$BENCH/lean-toolchain" "$BENCH/"config-*.json "$out/files/"
  [ -s "$out/verdicts.tsv" ] || printf 'theorem\texit\tseconds\toutcome\tlast_line\n' > "$out/verdicts.tsv"
  for t in fa fb fc fd fe; do
    grep -q "^Bench.$t$TAB" "$out/verdicts.tsv" && continue
    one_comparator "$BENCH" "config-$t.json" "$out/Bench.$t" "Bench.$t" "$out/verdicts.tsv" 3600
  done
  chown -R "$LUSER:$LUSER" "$out"
}

build_target() {     # build_target LABEL TARGET...:  lake build, its log, one row of results-full/BUILDS.tsv
  local label=$1 t0 rc; shift; t0=$(date +%s)
  asl bash -c 'cd "$1" && shift && lake build "$@"' _ "$LEANDIR" "$@" > "$LOGS/build-${label// /-}.log" 2>&1; rc=$?
  [ -s "$RES/BUILDS.tsv" ] || printf 'build\texit\tseconds\ttargets\n' > "$RES/BUILDS.tsv"
  printf '%s\t%s\t%s\t%s\n' "$label" "$rc" "$(( $(date +%s) - t0 ))" "$#" >> "$RES/BUILDS.tsv"
  return 0           # a module that does not build is a result:  the stages that read it record it per challenge
}

runall() {           # runall OUTDIR SIDE:  scripts/run_all.py on every challenge, runall-jobs copies on disjoint lists
  local out=$1 side=$2 j mem ram k list all missing pids=() p
  j=$(setting runall-jobs 1); [[ $j =~ ^[0-9]+$ ]] && [ "$j" -ge 1 ] || j=1
  ram=$(awk '/MemTotal/{print int($2/1024)}' /proc/meminfo)
  mem=$(( ram * 3 / 4 / j )); [ "$mem" -gt 16384 ] && mem=16384
  mkdir -p "$out" && chown "$LUSER:$LUSER" "$out"
  all=$(names)
  for k in $(seq 0 $((j - 1))); do
    list=$(printf '%s\n' "$all" | awk -v j="$j" -v k="$k" '(NR - 1) % j == k' | paste -sd, -)
    [ -n "$list" ] || continue
    asl bash -c 'cd "$1" && python3 -I scripts/run_all.py sources/openai-math/lean ../da2/discipline/lean "$2" \
                   --side="$3" --mem="$4" --skip-done --only="$5"' _ "$CS" "$out" "$side" "$mem" "$list" \
      >> "$LOGS/runall-$side-$k.log" 2>&1 &
    pids+=($!)
  done
  for p in "${pids[@]}"; do wait "$p"; done
  # every challenge is in the denominator:  one without its meta.json is listed, and the stage is not done
  missing=$(printf '%s\n' "$all" | while read -r n; do [ -e "$out/$n/meta.json" ] || echo "$n"; done)
  if [ -n "$missing" ]; then printf '%s\n' "$missing" > "$out/MISSING.txt"; echo "no meta.json: $missing"; return 1; fi
  rm -f "$out/MISSING.txt"
}

stage_chalbuild() { needs deps > "$STATE/chalbuild.why" || return 3; build_target "challenge files" ComparatorChallenges; }
stage_chalside()  { needs chalbuild > "$STATE/chalside.why" || return 3; runall "$RES/challenge-side" challenge; }
stage_solbuild() {
  needs deps > "$STATE/solbuild.why" || return 3
  if [ "$(setting build-scope challenges)" = library ]; then build_target "library" OAI; return; fi
  local mods; mapfile -t mods < <(jq -r .solution_module "$LEANDIR"/ComparatorChallenges/*.json | sort -u)
  build_target "solution modules" "${mods[@]}"
}
stage_solside()   { needs solbuild > "$STATE/solside.why" || return 3; runall "$RES" solution; }

stage_comparator() { # real Comparator on every config (CLOUD-PLAN 5);  verdicts in results-full/comparator/summary.tsv
  needs tools deps chalbuild solbuild > "$STATE/comparator.why" || return 3
  cmp_ready > "$STATE/comparator.why" || return 3
  local out="$RES/comparator" p cpus ram missing
  mkdir -p "$out" && chown "$LUSER:$LUSER" "$out"
  [ -s "$out/summary.tsv" ] || printf 'challenge\texit\tseconds\toutcome\tlast_line\n' > "$out/summary.tsv"
  cpus=$(nproc); ram=$(awk '/MemTotal/{print int($2/1048576)}' /proc/meminfo)
  p=$(( cpus / 4 )); [ $(( ram / 16 )) -lt "$p" ] && p=$(( ram / 16 )); [ "$p" -ge 1 ] || p=1
  echo "Comparator runs at once: $p"
  names | while read -r n; do grep -q "^$n$TAB" "$out/summary.tsv" || echo "$n"; done | xargs -r -P "$p" -n 1 "$SELF" cmp-one
  missing=$(names | while read -r n; do grep -q "^$n$TAB" "$out/summary.tsv" || echo "$n"; done)
  [ -z "$missing" ] || { echo "no verdict row: $missing"; return 1; }
}

# --- boot and the service ----------------------------------------------------------------------------------------------
boot() {
  mkdir -p "$STATE"
  # the copy the service runs:  this script as the metadata holds it (the runner's temporary copy as a fallback)
  { meta attributes/startup-script > "$SELF.new" && [ -s "$SELF.new" ]; } || cp "$0" "$SELF.new"
  chmod 0755 "$SELF.new" && mv -f "$SELF.new" "$SELF"
  sysctl -q -w vm.max_map_count=262144
  guard_metadata
  [ -e "$STATE/ALL.done" ] && { say "the run is finished;  nothing to do"; exit 0; }
  systemctl is-active -q oai-run && exit 0
  systemctl reset-failed oai-run 2>/dev/null
  systemd-run --unit=oai-run -p LimitNOFILE=1048576 -p StandardOutput=append:/var/log/oai-run.log \
    -p StandardError=append:/var/log/oai-run.log "$SELF" work
}

work() {
  exec 8> "$STATE/work.lock"; flock -n 8 || { say "another run holds the lock"; exit 0; }
  mkdir -p "$LOGS"
  say "work: start"
  ( while sleep 1800; do publish "full run: progress $(ts)"; done ) &
  local pub=$! s all=1
  for s in "${STAGES[@]}"; do run_stage "$s"; done
  kill "$pub" 2>/dev/null
  for s in "${STAGES[@]}"; do [ -e "$STATE/$s.done" ] || [ -e "$STATE/$s.skipped" ] || all=0; done
  echo "- this boot's pass ended: $(ts);  every stage done: $([ $all = 1 ] && echo yes || echo no)" >> "$LOGS/RUN-INFO.md"
  publish "full run: $([ $all = 1 ] && echo 'every stage done' || echo 'pass ended, stages not done (logs/full-run/STAGES.tsv)')"
  [ $all = 1 ] && touch "$STATE/ALL.done"
  if [ "$(setting stop-when-done yes)" = yes ]; then say "stopping the machine"; shutdown -h +1; fi
}

[ "${OAI_VM_SOURCE_ONLY:-}" = 1 ] && return 0
case "${1:-boot}" in
  boot)    boot ;;
  work)    work ;;
  cmp-one) one_comparator "$LEANDIR" "ComparatorChallenges/$2.json" "$RES/comparator/$2" "$2" \
             "$RES/comparator/summary.tsv" "$(setting comparator-timeout 10800)" ;;
  *)       echo "usage: $0 [boot | work | cmp-one NAME]"; exit 2 ;;
esac
