#!/bin/bash
# Enumerator for root-cause.md section 1: first-parent main commits since
# 2026-09-17, and how many of them added bare claim lines to either claim file.
cnt(){ git show "$1:$2" 2>/dev/null | awk -F'#' '$1 ~ /[^ \t]/' | wc -l; }
tot=0; n=0
for c in $(git rev-list --first-parent --since=2026-09-17 ${1:-f67f598a}); do
  tot=$((tot+1)); p=$(git rev-parse $c^1)
  a=$(( $(cnt $c tests/golden/claimed_drift.txt)+$(cnt $c tests/golden/card_claimed_drift.txt) ))
  if [ $a -gt 0 ] && git diff $p $c -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt | grep -q '^+[^+#]'; then n=$((n+1)); fi
done
echo "first-parent: $tot claim-adding: $n"
