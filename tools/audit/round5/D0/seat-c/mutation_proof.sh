#!/bin/sh
# D0-c mutation proof: break the fix four ways, one knob at a time, and print
# the checks that go red.  Runs the SHIPPED tests/optimality.py from the
# mutation checkout, so the proof is about the branch's own text and cannot
# drift from it.
#
# COMMAND (from the tree root; MUT is a git checkout of this branch):
#   sh tools/audit/round5/D0/seat-c/mutation_proof.sh <MUT> <out-dir>
#
# EXPECTED: M2p 1 red (#1294 cut), M2s 2 red (#1294 cut + seed counts), M2 2 red
# (the same two), M3 1 red (#1295), nothing else moving in any run.  M2s reddens
# the cut check too because removing the appended candidate leaves production
# and the seeds-kept/cut-4 arm as the same configuration: the pair is what
# ships, not either half.  #1293's stop-rule knob is not in this diff and has no
# mutation here.
set -u
MUT=$1
OUT=$2
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT"
for M in M2p_cut_only M2s_seeds_only M2_seeds_and_cut M3_warm_none; do
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
