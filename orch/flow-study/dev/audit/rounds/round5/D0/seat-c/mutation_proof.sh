#!/bin/sh
# D0-c mutation proof: break the shipped knob, and print the checks that go red.
# Runs the SHIPPED tests/optimality.py from the mutation checkout, so the proof
# is about the branch's own text and cannot drift from it.
#
# COMMAND (from the tree root; MUT is a git checkout of this branch):
#   sh tools/audit/round5/D0/seat-c/mutation_proof.sh <MUT> <out-dir>
#
# EXPECTED: M3 1 red -- the #1295 extra-candidate check, whose first seam call
# then carries one candidate fewer -- and nothing else moving.  The no-worse
# check does NOT move under M3: with the knob off both arms are the same run, so
# its bound is satisfied by equality.  It is the DIRECTIONAL guarantee the old
# percentage check was re-cut into, an invariant of _multi_start_minimize rather
# than a discriminator; mutate.py's docstring says the same.  The three M2
# mutations that reverted #1294's cut and its two appended seeds were removed
# with the finding: their source literals are no longer in the tree, so an
# exact-string substitution refuses on them by design and the harness would
# report a failure of the prover rather than of the fix.  #1293's stop-rule knob
# is not in this diff and has no mutation here.
set -u
MUT=$1
OUT=$2
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT"
for M in M3_warm_none; do
    echo "### $M"
    git -C "$MUT" checkout -- custom_components/heatpump_optimizer/optimizer.py
    python3 "$HERE/mutate.py" "$MUT" "$M" || exit 1
    (
        cd "$MUT" &&
        PYTHONPATH="$MUT/tests/hastub" python3 -u tests/optimality.py
    ) > "$OUT/$M.txt" 2>&1
    echo "exit=$?"
    grep -E "^  FAIL|OPTIMALITY CHECKS" "$OUT/$M.txt"
done
git -C "$MUT" checkout -- custom_components/heatpump_optimizer/optimizer.py
echo "restored; mutations done"
