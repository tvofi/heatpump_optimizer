#!/bin/bash
# My instrument: step 6g's cost at a given prepr.sh extraction, measured as the
# step itself runs it -- a narrow copy, then claims_reg_line on that copy.
# CPU is user+sys (load-independent); wall is reported with the load beside it.
# Usage: time6g.sh <block-file> <repo> <changed-paths file> <runs> <tag>
set -uo pipefail
BLOCK=$1; REPO=$2; CH=$3; N=${4:-3}; TAG=${5:-x}
. "$BLOCK"
export CLAIMS_GEN CLAIMS_DOCS CLAIMS_INPUTS
cd "$REPO" || exit 2
for i in $(seq 1 "$N"); do
  T=$(mktemp -d)
  /usr/bin/time -p bash -c 'git archive HEAD -- $CLAIMS_INPUTS "$CLAIMS_GEN" | tar -x -C "$1"' _ "$T" 2>"$T.cp"
  /usr/bin/time -p bash -c '. '"$BLOCK"'; export CLAIMS_GEN CLAIMS_DOCS; cd '"$REPO"' && claims_reg_line "$1" "$2"' _ "$CH" "$T" >"$T.out" 2>"$T.fn"
  rc=$?
  read -r cw cc <<<"$(awk '/^real/{r=$2}/^user/{u=$2}/^sys/{s=$2}END{print r, u+s}' "$T.cp")"
  read -r fw fc <<<"$(awk '/^real/{r=$2}/^user/{u=$2}/^sys/{s=$2}END{print r, u+s}' "$T.fn")"
  tot=$(awk -v a="$cc" -v b="$fc" 'BEGIN{printf "%.2f", a+b}')
  echo "$TAG run$i rc=$rc copy_cpu=$cc fn_cpu=$fc total_cpu=$tot copy_wall=$cw fn_wall=$fw load=$(sysctl -n vm.loadavg | tr -d '{}' | awk '{print $1}')"
  echo "   line: $(tail -1 "$T.out")"
  rm -rf "$T" "$T.cp" "$T.fn" "$T.out"
done
