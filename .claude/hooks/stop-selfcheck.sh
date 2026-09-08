#!/bin/bash
# Stop. Refuses to let a seat end its turn with the policy corpus red, when the
# turn touched the policy corpus.
#
# WHY A STOP HOOK AND NOT A RULE. `prepr.sh` exists, `pr-contract` re-executes
# it, and neither runs at the moment a seat decides it is finished. The measured
# failure is not "the seat did not know" -- it is "the seat knew and the check
# ran after the push". Process state (b): the process existed and was not
# followed. A Stop hook is the only surface that fires exactly then.
#
# SCOPED, so an ordinary code turn pays nothing. It runs only when the branch's
# three-dot diff touches a policy or workflow path, which is the same set
# `policy_lint` measures. On every other turn it exits 0 having run `git diff
# --name-only`, which is milliseconds.
#
# IT FIRES ONCE. `stop_hook_active` is true when a previous Stop hook already
# forced this turn to continue; re-firing then would loop a seat that cannot fix
# the finding. So the second pass through always exits 0 and says so -- the
# refusal is a prompt to look, not a cage.
#
#   .claude/hooks/stop-selfcheck.sh --self-test
set -uo pipefail

# The paths whose contents `policy_lint` and the governance workflow measure.
# Deliberately a PREFIX list rather than the linter's own globs: this decides
# whether to RUN the linter, so it may be wider than what the linter reads, and
# a prefix that is too narrow is the failure that matters.
POLICY_PREFIXES='^(CLAUDE\.md|\.claude/|\.cursor/|tools/audit/|tests/README\.md|docs/HANDOVER\.md|\.github/)'

touches_policy() { # $1 the newline-separated changed-file list
  printf '%s\n' "$1" | grep -qE "$POLICY_PREFIXES"
}

active() { # $1 the raw payload -- true when a Stop hook already continued this turn
  python3 - "$1" <<'PY'
import json, sys
try:
    print("yes" if json.loads(sys.argv[1]).get("stop_hook_active") else "no")
except Exception:
    print("no")
PY
}

if [ "${1:-}" = "--self-test" ]; then
  pass=0; fail=0
  st() { if [ "$1" = "$2" ]; then pass=$((pass+1)); printf '  ok   %s\n' "$3"
         else fail=$((fail+1)); printf '  FAIL %s (got %s, wanted %s)\n' "$3" "$1" "$2"; fi; }

  touches_policy 'custom_components/heatpump_optimizer/const.py'; st $? 1 "a production-only turn does not run the linter"
  touches_policy 'tests/plan_prices.py'                        ; st $? 1 "a suite-only turn does not run the linter"
  touches_policy 'CLAUDE.md'                                   ; st $? 0 "a CLAUDE.md turn runs it"
  touches_policy '.claude/rules/gate-scoping.md'               ; st $? 0 "a rule turn runs it"
  touches_policy 'tools/audit/briefs/fixer.md'                 ; st $? 0 "a contract turn runs it"
  touches_policy '.github/workflows/governance.yml'            ; st $? 0 "a workflow turn runs it"
  touches_policy 'docs/HANDOVER.md'                            ; st $? 0 "the handover runs it"
  touches_policy 'docs/plan-2026-09-open-issues.md'            ; st $? 1 "another docs/ file does not -- only the handover is policy there"
  printf 'a\ncustom_components/x.py\n.claude/rules/y.md\nb\n' >/dev/null
  touches_policy "$(printf 'custom_components/x.py\n.claude/rules/y.md')"; st $? 0 "one policy path among several is enough"

  st "$(active '{"stop_hook_active":true}')"  yes "stop_hook_active true is read"
  st "$(active '{"stop_hook_active":false}')" no  "stop_hook_active false is read"
  st "$(active '{}')"                         no  "an absent flag reads as not-active"
  st "$(active 'not json')"                   no  "an unparseable payload reads as not-active (fail open, one refusal at most)"

  printf '\n%s passed, %s failed\n' "$pass" "$fail"
  [ "$fail" -eq 0 ] || exit 2
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
PAYLOAD=$(cat)
[ "$(active "$PAYLOAD")" = yes ] && exit 0

BASE=$(git merge-base origin/main HEAD 2>/dev/null) || exit 0
[ -n "$BASE" ] || exit 0
CHANGED=$(git diff --name-only "$BASE"...HEAD 2>/dev/null; git diff --name-only 2>/dev/null)
touches_policy "$CHANGED" || exit 0

# No node, no verdict. Refusing a turn because the checker is absent would
# block a seat on a fact about its box rather than about its diff.
command -v node >/dev/null 2>&1 || exit 0
OUT=$(node .claude/workflows/policy_lint.mjs 2>&1); RC=$?
[ "$RC" -eq 0 ] && exit 0
printf 'stop-selfcheck: this turn touched the policy corpus and policy_lint refuses it.\n%s\n\nRun `bash tools/audit/prepr.sh` before opening or updating a pull request.\n' \
  "$(printf '%s' "$OUT" | grep -E '^\s+(ERROR|WARN)|^TOTAL' | head -20)" >&2
exit 2
