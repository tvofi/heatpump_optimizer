#!/bin/bash
# Adversarial re-review of #2853: drive step 6g's blocked scenario both ways.
# Usage: drive.sh <head-ref> <block-file> <tag>
set -uo pipefail
REF=$1; BLOCK=$2; TAG=$3
ROOT=/tmp/rev2853r2
FX=$ROOT/fx-$TAG
NARROW=$ROOT/narrow-$TAG
WHOLE=$ROOT/whole-$TAG
rm -rf "$FX" "$NARROW" "$WHOLE"
mkdir -p "$FX" "$NARROW" "$WHOLE"
git -C ${WT:-$HOME/hpo-seats/r10s6/wt-2853-r2} archive "$REF" | tar -x -C "$FX"
( cd "$FX" || exit 2
  git init -q -b main
  git config user.name review; git config user.email review@example.invalid
  git add -A >/dev/null 2>&1
  git commit -qm "fixture base $REF"
)
# the round-1 edit shape: one in-tree link to a file outside CLAIMS_INPUTS
printf '\n- [instruments](../tools/audit/seat/INSTRUMENTS.md)\n' >> "$FX/docs/architecture.md"
# re-record the register at the repo root on the full tree
( cd "$FX" && PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py > "$ROOT/rec-$TAG.out" 2>&1 )
echo "== [$TAG] generator at repo root rc=$? =="
grep -m1 '^C108' "$ROOT/rec-$TAG.out" | sed 's/^/   /'
( cd "$FX" && git add -A && git commit -qm "fixture: doc link outside CLAIMS_INPUTS, register re-recorded on the full tree" )
( cd "$FX" && git log --oneline -1 )
# shellcheck disable=SC1090
. "$BLOCK"
export CLAIMS_GEN
# the copy exactly as step 6g builds it (its own constants)
( cd "$FX" && git archive HEAD -- $CLAIMS_INPUTS "$CLAIMS_GEN" | tar -x -C "$NARROW" )
( cd "$FX" && git archive HEAD | tar -x -C "$WHOLE" )
printf 'docs/architecture.md\n' > "$ROOT/changed-$TAG"
echo "== [$TAG] narrow copy KB: $(du -sk "$NARROW" | cut -f1) =="
line=$( cd "$FX" && claims_reg_line "$ROOT/changed-$TAG" "$NARROW" ); r=$?
echo "== [$TAG] NEW step copy: rc=$r :: $line"
line=$( cd "$FX" && claims_reg_line "$ROOT/changed-$TAG" "$WHOLE" ); r=$?
echo "== [$TAG] whole-tree copy (control): rc=$r :: $line"
echo "== [$TAG] target present in narrow copy: $( [ -e "$NARROW/tools/audit/seat/INSTRUMENTS.md" ] && echo yes || echo no )"
