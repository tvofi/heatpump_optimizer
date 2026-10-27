#!/bin/bash
# Perturbation: the per-target `python3 -I -c` replaced by in-shell normalisation.
# Cost must fall under the budget; the graded verdicts must not move.
set -uo pipefail
. /tmp/rev2853r2/claims_block_fast.sh
export CLAIMS_GEN
FX=/tmp/rev2853r2/fx-new
printf 'docs/architecture.md\n' > /tmp/rev2853r2/ch.paths
cd "$FX" || exit 2
for i in 1 2 3; do
  T=$(mktemp -d)
  git archive HEAD -- $CLAIMS_INPUTS "$CLAIMS_GEN" | tar -x -C "$T"
  /usr/bin/time -p bash -c '. /tmp/rev2853r2/claims_block_fast.sh; claims_reg_line /tmp/rev2853r2/ch.paths '"$T" > "$T.out" 2> "$T.time"
  rc=$?
  awk -v rc="$rc" '/^real/{r=$2}/^user/{u=$2}/^sys/{s=$2}END{print "fast run'"$i"' rc="rc" real",r,"cpu",u+s}' "$T.time"
  echo "  $(tail -1 "$T.out")"
  rm -rf "$T"
done
# the class-open arm: unlisted target derived?
T=$(mktemp -d); git archive HEAD -- $CLAIMS_INPUTS "$CLAIMS_GEN" | tar -x -C "$T"
cd "$FX" && . /tmp/rev2853r2/claims_block_fast.sh
claims_reg_line /tmp/rev2853r2/ch.paths "$T" > "$T.out" 2>&1; rc=$?
echo "arm unlisted-target rc=$rc target_present=$([ -e "$T/tools/audit/seat/INSTRUMENTS.md" ] && echo yes || echo no)"
rm -rf "$T"
# the repository-lacks-target arm (p1)
T=$(mktemp -d); cd /tmp/rev2853r2/p1
git archive HEAD -- $CLAIMS_INPUTS "$CLAIMS_GEN" | tar -x -C "$T"
. /tmp/rev2853r2/claims_block_fast.sh
claims_reg_line /tmp/rev2853r2/ch.paths "$T" > "$T.out" 2>&1; rc=$?
echo "arm target-absent rc=$rc :: $(tail -1 "$T.out")"
rm -rf "$T"
