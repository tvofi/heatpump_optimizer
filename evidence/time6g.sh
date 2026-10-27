#!/bin/bash
# Re-measure prepr.sh step 6g (claims_reg_line over the narrowed copy), CPU and wall.
# Usage: time6g.sh <worktree> <runs>
set -uo pipefail
WT=$1
N=${2:-3}
cd "$WT" || exit 2
. /tmp/rev2853-tools/claims_block.sh
export CLAIMS_INPUTS CLAIMS_GEN
for i in $(seq 1 "$N"); do
  T=$(mktemp -d)
  printf 'docs/x.md\n' > "$T.paths"
  /usr/bin/time -p bash -c 'git archive HEAD -- $CLAIMS_INPUTS "$CLAIMS_GEN" | tar -x -C "$1"' _ "$T" 2> "$T.copy.time"
  cpy_rc=$?
  /usr/bin/time -p bash -c '. /tmp/rev2853-tools/claims_block.sh; claims_reg_line "$1.paths" "$1"' _ "$T" > "$T.out" 2> "$T.fn.time"
  fn_rc=$?
  cr=$(awk '/^real/{r=$2} /^user/{u=$2} /^sys/{s=$2} END{print r, u+s}' "$T.copy.time")
  fr=$(awk '/^real/{r=$2} /^user/{u=$2} /^sys/{s=$2} END{print r, u+s}' "$T.fn.time")
  echo "run$i copy_rc=$cpy_rc copy_wall_cpu=$cr fn_rc=$fn_rc fn_wall_cpu=$fr load=$(sysctl -n vm.loadavg 2>/dev/null | tr -d '{}')"
  echo "  line: $(tail -1 "$T.out")"
  echo "  size_kb: $(du -sk "$T" | cut -f1)"
  rm -rf "$T" "$T.paths"
done
