#!/bin/bash
# drive6g.sh <prepr.sh to extract from> <repo checkout at the commit to grade> <changed-paths file> [whole]
# Extracts pinned_touched, CLAIMS_*, claims_reg_line unchanged from the given prepr.sh,
# builds the copy step 6g builds (git archive HEAD -- CLAIMS_INPUTS CLAIMS_GEN), or the whole tree with "whole",
# runs claims_reg_line, prints "RC=<n> <line>" and CPU of copy+function.
P=$1; REPO=$2; CH=$3; MODE=${4:-narrow}
F=$(mktemp); { sed -n '/^pinned_touched() {/,/^}/p' "$P"; sed -n '/^CLAIMS_DOCS=/,/^claims_reg_line() {/p' "$P" | sed '$d'; sed -n '/^claims_reg_line() {/,/^}/p' "$P"; } > "$F"
source "$F"; rm -f "$F"
cd "$REPO" || exit 9
CR=$(mktemp -d)
t0=$(cat /proc/$$/stat | awk '{print $14+$15+$16+$17}')
if [ "$MODE" = whole ]; then git archive HEAD | tar -x -C "$CR"; else git archive HEAD -- $CLAIMS_INPUTS "$CLAIMS_GEN" | tar -x -C "$CR"; fi
L=$(claims_reg_line "$CH" "$CR"); rc=$?
t1=$(cat /proc/$$/stat | awk '{print $14+$15+$16+$17}')
echo "RC=$rc $L"
echo "CPU_TICKS=$((t1-t0)) (1/$(getconf CLK_TCK) s, self+children)"
rm -rf "$CR"
