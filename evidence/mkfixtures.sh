#!/bin/bash
# Rebuilds the four fixtures this review drove, from the reviewed head.
# A: a doc link to an in-tree file outside CLAIMS_INPUTS (the class-open shape).
# B: a `docs/../` link to an in-tree file outside CLAIMS_INPUTS (the shape where
#    os.path.normpath and the shell form differ).
# C: A's link added without re-recording the register (the stale arm).
# D: A with the link's target deleted from the repository (the absent arm).
# Usage: mkfixtures.sh <worktree at the reviewed head> <output dir>
set -uo pipefail
WT=$1; OUT=${2:-$HOME/hpo-seats/r10s6/review-2853-r4-ev/work}
mkdir -p "$OUT"
for f in A B C D; do
  rm -rf "$OUT/$f"; mkdir -p "$OUT/$f"
  git -C "$WT" archive HEAD | tar -x -C "$OUT/$f"
  ( cd "$OUT/$f" && git init -q -b main && git config user.name review \
    && git config user.email review@example.invalid && git add -A && git commit -qm "fixture base" )
done
printf '\n- [instruments](../tools/audit/seat/INSTRUMENTS.md)\n' >> "$OUT/A/docs/architecture.md"
printf '\n- [prepr](../tools/pr/prepr.sh)\n'                   >> "$OUT/B/docs/architecture.md"
printf '\n- [instruments](../tools/audit/seat/INSTRUMENTS.md)\n' >> "$OUT/C/docs/architecture.md"
for f in A B; do ( cd "$OUT/$f" && PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py >/dev/null 2>&1 \
  && git add -A && git commit -qm "re-recorded on the full tree" ); done
( cd "$OUT/C" && git add -A && git commit -qm "link added, register not re-recorded" )
cp -a "$OUT/A/." "$OUT/D/"; ( cd "$OUT/D" && git rm -q tools/audit/seat/INSTRUMENTS.md && git commit -qm "target removed" )
for f in A B C D; do echo "$f $(git -C "$OUT/$f" rev-parse --short HEAD)"; done
