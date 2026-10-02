#!/bin/bash
# Reviewer's simulation (round 3). sim2 = PR head 1517fa2d merged onto (main aab94eea + precursor 07b0704b) = B1.
export PATH=/Users/timmalmstrom/hpo-seats/bin:$PATH RUNNER_TEMP=/Users/timmalmstrom/hpo-seats/1847-review/rt
cd /Users/timmalmstrom/hpo-seats/1847-review/sim2
B1=50eb80642e0116ec97067372f3e5a2c8d3c019f4; M2=$(git rev-parse HEAD); MAIN=aab94eea2211b41a224fd23980e084e77c529ec0
pin() { git reset -q; git checkout -q HEAD -- .; git checkout -q "$1" -- '.claude/workflows/*.mjs' '.claude/workflows/*.py' 'tools/audit/*.sh' 'tools/audit/record-predicate' 'tools/audit/round6/D11/fix/codeowners_gap.py' 'tests/coverage_ratchet.py' 'tests/entities.py' 'tests/gate_lock.py' 'tests/issue996_count.py' 'tests/nightly_ha.py' 'tests/replay.py' 'tests/structure.py' 'tools/audit/round4/D11/d11lib.py' 'tools/audit/round4/D11/governance_cost.py'; echo "-- pinned from $1: $(git diff --cached --name-only | wc -l) file(s) differ"; }
guard() { PINNED=$1 bash ../ev/guard_step.sh 2>&1 | grep -E 'skipped|RESULT|AGREEMENT'; echo "guard step (PINNED=$1) rc=${PIPESTATUS[0]}"; }
echo "== A. base = main+precursor (B1): what CI sees after the precursor merges"
pin $B1
node .claude/workflows/check-wave-script.mjs >/dev/null 2>&1; echo "check-wave-script rc=$?"
guard $B1
node .claude/workflows/agreement.mjs --self-test >/dev/null 2>&1; echo "lane self-test rc=$?"
node .claude/workflows/field_coverage.mjs 2>&1 | grep -E 'RESULT'; echo "field_coverage rc=${PIPESTATUS[0]}"
node .claude/workflows/policy_lint.mjs >/dev/null 2>&1; echo "policy_lint rc=$?"
echo "== B. base = current main (aab94eea), guard only"
pin $MAIN; guard $MAIN
echo "== C. base carries the lane (M2, i.e. after #1847 merges): guard must NOT skip"
pin $M2; guard $M2
echo "== D. same base, perturbed: CLASS_GUESS grammar mutant in audit-find.js (a reader the lane reads, not pinned) -> must go red, not skip"
perl -pi -e 's{^const CLASS_GUESS = /\^\(I1\|.*$}{const CLASS_GUESS = /^([PI][0-9]+|new)\$/}' .claude/workflows/audit-find.js; git diff --stat -- .claude/workflows/audit-find.js | tail -1
guard $M2
echo "== E. same mutant, base lacking the lane (main): the guard skips (the bootstrap window only)"
guard $MAIN
pin $M2; git reset -q; git checkout -q HEAD -- .; git status --short | head
