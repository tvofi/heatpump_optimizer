#!/bin/bash
# Re-measure step 6g at the reviewed head: narrow copy + the head's own claims_reg_line.
# Usage: time6g-r2.sh <fixture repo> <runs>
set -uo pipefail
FX=$1
N=${2:-3}
BLOCK=/tmp/rev2853r2/claims_block_new.sh
# shellcheck disable=SC1090
. "$BLOCK"
export CLAIMS_GEN CLAIMS_INPUTS CLAIMS_DOCS
cd "$FX" || exit 2
for i in $(seq 1 "$N"); do
  T=$(mktemp -d)
  printf 'docs/architecture.md\n' > "$T.paths"
  /usr/bin/time -p bash -c 'git archive HEAD -- $CLAIMS_INPUTS "$CLAIMS_GEN" | tar -x -C "$1"' _ "$T" 2> "$T.copy.time"
  /usr/bin/time -p bash -c '. /tmp/rev2853r2/claims_block_new.sh; claims_reg_line "$1.paths" "$1"' _ "$T" > "$T.out" 2> "$T.fn.time"
  fr=$?
  cr=$(awk '/^real/{r=$2} /^user/{u=$2} /^sys/{s=$2} END{print r, u+s}' "$T.copy.time")
  fn=$(awk '/^real/{r=$2} /^user/{u=$2} /^sys/{s=$2} END{print r, u+s}' "$T.fn.time")
  echo "run$i rc=$fr copy_wall_cpu=$cr fn_wall_cpu=$fn load=$(sysctl -n vm.loadavg 2>/dev/null | tr -d '{}')"
  echo "  line: $(tail -1 "$T.out")"
  rm -rf "$T" "$T.paths"
done
