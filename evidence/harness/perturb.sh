#!/bin/bash
# Perturbations on step 6g at the new head.
set -uo pipefail
ROOT=/tmp/rev2853r2
BLOCK=$ROOT/claims_block_new.sh
. "$BLOCK"
export CLAIMS_GEN
run() { # repo copy changed
  ( cd "$1" && claims_reg_line "$3" "$2" ); echo "rc=$?"
}
# P2: a SECOND unlisted target, different path
P2=$ROOT/p2
rm -rf "$P2"; cp -a "$ROOT/fx-new" "$P2"
printf '\n- [prepr](https://example.invalid/x) [prepr](../tools/pr/prepr.sh)\n' >> "$P2/docs/architecture.md"
( cd "$P2" && PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py >/dev/null 2>&1 && git add -A && git commit -qm "p2: second unlisted target" )
rm -rf "$ROOT/p2copy"; mkdir -p "$ROOT/p2copy"
( cd "$P2" && git archive HEAD -- $CLAIMS_INPUTS "$CLAIMS_GEN" | tar -x -C "$ROOT/p2copy" )
echo "== P2 second unlisted target (../tools/pr/prepr.sh) =="; run "$P2" "$ROOT/p2copy" "$ROOT/changed-new"
echo "   target present: $( [ -e "$ROOT/p2copy/tools/pr/prepr.sh" ] && echo yes || echo no )"

# P1: target the repository lacks (link kept, file removed)
P1=$ROOT/p1
rm -rf "$P1"; cp -a "$ROOT/fx-new" "$P1"
( cd "$P1" && git rm -q tools/audit/seat/INSTRUMENTS.md && git commit -qm "p1: target removed from the repository" )
rm -rf "$ROOT/p1copy"; mkdir -p "$ROOT/p1copy"
( cd "$P1" && git archive HEAD -- $CLAIMS_INPUTS "$CLAIMS_GEN" | tar -x -C "$ROOT/p1copy" )
echo "== P1 link whose target the repository lacks =="; run "$P1" "$ROOT/p1copy" "$ROOT/changed-new"

# P4: stale register (link added, register not re-recorded)
P4=$ROOT/p4
rm -rf "$P4"; mkdir -p "$P4"
git -C ${WT:-$HOME/hpo-seats/r10s6/wt-2853-r2} archive fccb883716ce7f8677ea64a2107971baa5381ea9 | tar -x -C "$P4"
( cd "$P4" && git init -q -b main && git config user.name r && git config user.email r@e.invalid && git add -A && git commit -qm base )
printf '\n- [instruments](../tools/audit/seat/INSTRUMENTS.md)\n' >> "$P4/docs/architecture.md"
( cd "$P4" && git add -A && git commit -qm "p4: link added without re-recording" )
rm -rf "$ROOT/p4copy"; mkdir -p "$ROOT/p4copy"
( cd "$P4" && git archive HEAD -- $CLAIMS_INPUTS "$CLAIMS_GEN" | tar -x -C "$ROOT/p4copy" )
echo "== P4 stale register (link added, not re-recorded) =="; run "$P4" "$ROOT/p4copy" "$ROOT/changed-new"

# P5: link inside CLAIMS_INPUTS (tests/rolling.py is listed)
P5=$ROOT/p5
rm -rf "$P5"; cp -a "$ROOT/fx-new" "$P5"
printf '\n- [rolling](../tests/rolling.py)\n' >> "$P5/docs/architecture.md"
( cd "$P5" && PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py >/dev/null 2>&1 && git add -A && git commit -qm "p5: listed target" )
rm -rf "$ROOT/p5copy"; mkdir -p "$ROOT/p5copy"
( cd "$P5" && git archive HEAD -- $CLAIMS_INPUTS "$CLAIMS_GEN" | tar -x -C "$ROOT/p5copy" )
echo "== P5 link inside CLAIMS_INPUTS (../tests/rolling.py) =="; run "$P5" "$ROOT/p5copy" "$ROOT/changed-new"

# P6: clean tree, no docs change
printf 'tools/x.py\n' > "$ROOT/changed-none"
echo "== P6 no docs change =="; run "$ROOT/fx-new" /nonexistent "$ROOT/changed-none"

# P3: the derivation dropped (prepr-13's shape): force the guard false
sed 's|if \[ -f "\$repo/\$CLAIMS_GEN" \] && grep -q -e .--print-link-targets. "\$2/\$CLAIMS_GEN" 2>/dev/null; then|if false; then|' "$BLOCK" > "$ROOT/claims_block_noderive.sh"
grep -c 'if false; then' "$ROOT/claims_block_noderive.sh"
rm -rf "$ROOT/p3copy"; mkdir -p "$ROOT/p3copy"; ( cd "$ROOT/fx-new" && git archive HEAD -- $CLAIMS_INPUTS "$CLAIMS_GEN" | tar -x -C "$ROOT/p3copy" )
( cd "$ROOT" && . "$ROOT/claims_block_noderive.sh" && export CLAIMS_GEN && cd "$ROOT/fx-new" && claims_reg_line "$ROOT/changed-new" "$ROOT/p3copy" ); echo "rc=$?"
echo "   target present after no-derivation: $( [ -e "$ROOT/p3copy/tools/audit/seat/INSTRUMENTS.md" ] && echo yes || echo no )"
