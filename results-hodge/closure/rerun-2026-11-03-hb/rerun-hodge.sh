#!/bin/bash
# rerun-hodge.sh K MEM : rerun closure group K exactly as oai-hodge-vm.sh group does, into closure/rerun-2026-11-03
set -u
C=/srv/oai/casestudy/results-hodge/closure; O=$C/rerun-2026-11-03-hb; k=$1
m=$(awk -F'\t' -v k="$k" '$1 == k { print $2 }' "$C/GROUPS.tsv" | paste -sd, -)
export DISCIPLINE_LEAN_REGISTRY="$C/registry.tsv" REFEREE_MEM="$2"
export PATH=/home/lean/.elan/bin:/srv/oai/tools/bin:/usr/local/go/bin:/usr/local/bin:/usr/bin:/bin
cd /srv/oai/closure-root || exit 1
python3 -I /srv/oai/da2-hb/discipline/lean/referee_lean.py --project=. --modules="$m" --unfold-out="$O/unfold/group-$k" \
  > "$O/referee/group-$k.out" 2>&1
echo "exit $?" >> "$O/referee/group-$k.out"
python3 -I /srv/oai/da2-hb/discipline/lean/census/census.py --project=. --modules="$m" --out="$O/census/group-$k" \
  --referee-log="$O/referee/group-$k.out" > "$O/census/group-$k.out" 2>&1
echo "exit $?" >> "$O/census/group-$k.out"
