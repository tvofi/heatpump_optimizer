#!/bin/bash
# Re-measure the reviewed head's step 6g: whole-tree archive + old claims_reg_line.
set -uo pipefail
WT=$1
N=${2:-3}
cd "$WT" || exit 2
awk 'NR>=243 && NR<=253 {print} NR>=281 && NR<=325 {print}' tools/pr/prepr.sh > /tmp/rev2853-tools/claims_block_old.sh
for i in $(seq 1 "$N"); do
  T=$(mktemp -d)
  printf 'docs/x.md\n' > "$T.paths"
  /usr/bin/time -p bash -c 'git archive HEAD | tar -x -C "$1"' _ "$T" 2> "$T.copy.time"
  cpy_rc=$?
  /usr/bin/time -p bash -c '. /tmp/rev2853-tools/claims_block_old.sh; claims_reg_line "$1.paths" "$1"' _ "$T" > "$T.out" 2> "$T.fn.time"
  fn_rc=$?
  cr=$(awk '/^real/{r=$2} /^user/{u=$2} /^sys/{s=$2} END{print r, u+s}' "$T.copy.time")
  fr=$(awk '/^real/{r=$2} /^user/{u=$2} /^sys/{s=$2} END{print r, u+s}' "$T.fn.time")
  echo "run$i copy_rc=$cpy_rc copy_wall_cpu=$cr fn_rc=$fn_rc fn_wall_cpu=$fr load=$(sysctl -n vm.loadavg 2>/dev/null | tr -d '{}')"
  echo "  line: $(tail -1 "$T.out")"
  rm -rf "$T" "$T.paths"
done
