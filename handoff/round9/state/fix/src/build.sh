set -e
# Regenerates the round-9 fix plan from data.py, standing.md and FIX-PLAN-head.md, then lints the
# roster against an origin/main tree. gen.py exits non-zero on any placement, cap, ownership,
# concurrency, barrier-order or sweep-count error.
S=/tmp/claude-0/-home-claude/1da41f8a-eb29-5a61-aca6-50a7738462b9/scratchpad
cd $S
python3 fixplan/gen.py fixplan-wt
cp fixplan-wt/.claude/workflows/wave-r9-groups.json fixplan-main/.claude/workflows/
(cd fixplan-main && git fetch -q origin main && test "$(git rev-parse HEAD)" = "$(git rev-parse FETCH_HEAD)" \
  || { echo "fixplan-main is not at origin/main"; exit 1; })
set +e
(cd fixplan-main && node .claude/workflows/brief_lint.mjs .claude/workflows/wave-r9-groups.json > $S/fixplan/lint-main.out 2>&1)
rc=$?
echo "lint rc=$rc"; tail -1 $S/fixplan/lint-main.out
exit $rc
