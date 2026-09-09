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

  # AND THE SCRIPT ITSELF, end to end. Every case above drives a helper; none
  # touches the wrapper that reads the payload, asks git what changed and turns
  # a red linter into an exit status -- and that wrapper is where pre-edit.sh
  # was inert TWICE with its helpers all green. Without the end-to-end cases, replacing
  # this file's final `exit 2` with `exit 0` leaves 13 of 13 passing and the
  # hook completely inert in production.
  #
  # A scratch repository rather than a seam in production code: the linter is a
  # stub whose exit status this test chooses, so the refusal path and the
  # null-control path are both driven for real.
  e2e() { # want-rc, project-dir, payload, label
    printf '%s' "$3" | CLAUDE_PROJECT_DIR="$2" bash "$0" >/dev/null 2>&1
    local got=$?
    if [ "$got" -eq "$1" ]; then pass=$((pass+1)); printf '  ok   %s\n' "$4"
    else fail=$((fail+1)); printf '  FAIL %s (rc %s, wanted %s)\n' "$4" "$got" "$1"; fi
  }
  # Same driver, but keeping stderr: the mutation-arm finding is REPORTED rather
  # than refused, so its whole effect lands on the stream `e2e` discards.
  e2e_err() { # want-rc, project-dir, want-hits, needle, label
    local err got n
    err=$(printf '{}' | CLAUDE_PROJECT_DIR="$2" bash "$0" 2>&1 >/dev/null); got=$?
    n=$(printf '%s' "$err" | grep -c -- "$4")
    if [ "$got" -eq "$1" ] && [ "$n" -eq "$3" ]; then pass=$((pass+1)); printf '  ok   %s\n' "$5"
    else fail=$((fail+1)); printf '  FAIL %s (rc %s want %s; %s hit(s) want %s)\n' "$5" "$got" "$1" "$n" "$3"; fi
  }
  T=$(mktemp -d)
  if [ -n "$T" ] && git -C "$T" init -q 2>/dev/null; then
    mkdir -p "$T/.claude/workflows"
    printf 'seed\n' >"$T/CLAUDE.md"; printf 'seed\n' >"$T/prod.py"
    git -C "$T" add -A >/dev/null 2>&1
    git -C "$T" -c user.email=t@t -c user.name=t commit -qm seed >/dev/null 2>&1
    git -C "$T" update-ref refs/remotes/origin/main HEAD
    LINT="$T/.claude/workflows/policy_lint.mjs"

    printf 'changed\n' >"$T/CLAUDE.md"           # a policy path, tracked and modified
    printf 'process.exit(1)\n' >"$LINT"
    e2e 2 "$T" '{}' "END TO END: a red corpus on a policy-touching turn exits 2"
    e2e 0 "$T" '{"stop_hook_active":true}' "END TO END: the second pass exits 0 with the corpus still red"
    printf 'process.exit(0)\n' >"$LINT"
    e2e 0 "$T" '{}' "END TO END: a green corpus exits 0 (null control)"

    printf 'seed\n' >"$T/CLAUDE.md"              # restore it; touch a non-policy path only
    printf 'changed\n' >"$T/prod.py"
    printf 'process.exit(1)\n' >"$LINT"
    e2e 0 "$T" '{}' "END TO END: a production-only turn exits 0 without consulting the linter"

    # A MUTATION ARM: a tracked, committed production file altered and left --
    # what a stopped fixer leaves between breaking a check and restoring it. The
    # turn must still END (it is a report, not a cage) and the path must be
    # NAMED. Both halves, because a report nobody prints is the same as none.
    # Green stub first: this case is about the REPORT. With the red stub from the
    # case above still in place, both arm cases FAIL outright -- rc 2 where 0 is
    # wanted, hit counts still right -- which #671's round 1 measured, correcting
    # my claim that they would pass silently. A red self-test is the honest
    # failure mode; the stub is still required, for the smaller reason.
    printf 'process.exit(0)\n' >"$LINT"
    mkdir -p "$T/custom_components/heatpump_optimizer"
    printf 'x = 1\n' >"$T/custom_components/heatpump_optimizer/optimizer.py"
    git -C "$T" add -A >/dev/null 2>&1
    git -C "$T" -c user.email=t@t -c user.name=t commit -qm arm >/dev/null 2>&1
    printf 'x = 2\n' >"$T/custom_components/heatpump_optimizer/optimizer.py"
    e2e_err 0 "$T" 1 'optimizer.py' "END TO END: a mutation arm is named and the turn still ends"
    git -C "$T" checkout -- custom_components/heatpump_optimizer/optimizer.py >/dev/null 2>&1
    e2e_err 0 "$T" 0 'optimizer.py' "END TO END: and nothing is said once the arm is restored (null control)"
    rm -rf "$T"
  else
    # A box without a working `git init` cannot drive these. Say so rather than
    # counting the end-to-end cases as silent passes: a skipped drive that claims its pins is the
    # defect decision 0004 is about.
    printf '  SKIP END TO END: no scratch repository could be built on this box\n'
  fi

  printf '\n%s passed, %s failed\n' "$pass" "$fail"
  [ "$fail" -eq 0 ] || exit 2
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
PAYLOAD=$(cat)
[ "$(active "$PAYLOAD")" = yes ] && exit 0

# A MUTATION ARM LEFT IN THE TREE, reported before anything else, because it is
# the one finding that survives the seat. `fixer.md` proves a check by breaking
# the thing it checks and restoring it; a seat stopped between those two steps
# leaves a PRODUCTION file altered in its worktree, and the alteration looks
# exactly like an edit. Measured on this repository: ten worktrees carried an
# uncommitted change at once, six of them a single production file in a
# mutation worktree.
#
# Reported, never refused. The seat may legitimately be mid-edit, and a Stop
# hook that blocks on work in progress is a cage. This one names the files and
# lets the turn end -- what it buys is that nobody discovers the mutation days
# later in someone else's diff.
DIRTY_PROD=$(git status --porcelain -- custom_components 2>/dev/null | grep -E '^( M|M |MM)' | cut -c4- | head -10)
if [ -n "$DIRTY_PROD" ]; then
  printf 'stop-selfcheck: production file(s) modified and uncommitted in this worktree:\n%s\n\nIf this is a mutation arm from a proof, restore it now -- `git checkout --` the\npaths above. A stopped seat leaves the arm behind and it reads as an edit.\n' \
    "$(printf '%s' "$DIRTY_PROD" | sed 's/^/  /')" >&2
fi

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
