#!/bin/bash
# Pre-PR self-check: everything a seat can refuse about its own branch before it
# asks anyone to look at it.
#
# WHY THIS EXISTS. `preflight.sh` reads a body for unmeasured claims. Nothing
# read the BRANCH. The 2026-09 governance audit measured the result: 55 percent
# of review verdicts blocked, a mean of 1.79 review rounds and one pull request
# at eleven, and the blocking reasons were dominated by things a script can
# decide -- a stale head SHA in the body, a claim file that should have been
# byte-identical, a MODE line nobody read, a carry destination that did not
# exist. A reviewer is the most expensive way to discover any of those.
#
# Every step refuses on non-zero. Run it before opening a pull request; the
# `pr-contract` job in .github/workflows/governance.yml re-executes the steps
# that are re-executable in CI, so the PRE-PR line this prints is a claim and
# the re-execution is the proof.
#
#   tools/audit/prepr.sh [body.md]
#
# Self-test (used by the `pr-contract` job, and by anyone changing this file):
#
#   tools/audit/prepr.sh --self-test
#
set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 2

# --- self-test ---------------------------------------------------------------
# A check that cannot be shown failing does not merge. This drives the two steps
# that are pure functions of their input -- the body checks -- against the rot
# fixtures, and asserts the healthy one stays silent. The branch-shape steps
# (merge base, gate mode, version edit, claim files) are demonstrated by the
# `pr-contract` job running this script on every pull request.
if [ "${1:-}" = "--self-test" ]; then
  D=.claude/workflows/fixtures/policy-rot/prepr
  ZERO=0000000000000000000000000000000000000000
  st_pass=0; st_fail=0
  st() { if [ "$1" = "$2" ]; then st_pass=$((st_pass+1)); printf '  ok   %s\n' "$3";
         else st_fail=$((st_fail+1)); printf '  FAIL %s (rc %s, wanted %s)\n' "$3" "$1" "$2"; fi; }

  for f in missing-section empty-section wrong-head dead-carry bad-friction backtick-bad-event bare-na folded-entry; do
    node .claude/workflows/policy_lint.mjs --pr-body "$D/$f.md" --head "$ZERO" >/dev/null 2>&1
    st $? 1 "a body with $f is refused"
  done
  node .claude/workflows/policy_lint.mjs --pr-body "$D/unnamed-red.md" --head "$ZERO" --red 'fast (3.14)' >/dev/null 2>&1
  st $? 1 "a body that does not name its red check is refused"
  # TWO null controls, not one. `good-none.md` answers every section with the
  # accepted WORD; `good.md` answers `## Friction` with a well-formed line. A
  # single fixture covering only `none` left the friction parser's accept path
  # unexercised, and the first real body written against this check was refused
  # for writing its rule id the way every other file in this corpus writes an
  # identifier. A rot fixture proves a check fires; only a healthy one that
  # exercises the same code path proves it fires for the right reason.
  node .claude/workflows/policy_lint.mjs --pr-body "$D/good.md" --head "$ZERO" >/dev/null 2>&1
  st $? 0 "a healthy body with a well-formed friction line is silent (null control)"
  node .claude/workflows/policy_lint.mjs --pr-body "$D/good-none.md" --head "$ZERO" >/dev/null 2>&1
  st $? 0 "a healthy body answering every section with a word is silent (null control)"

  printf 'Closes #999\n' | bash tools/audit/preflight.sh >/dev/null 2>&1
  st $? 1 "preflight refuses an unintended closing keyword"
  printf 'Closes #999\n' | bash tools/audit/preflight.sh 999 >/dev/null 2>&1
  st $? 0 "preflight accepts an intended one (null control)"

  printf '\n%s passed, %s failed\n' "$st_pass" "$st_fail"
  [ "$st_fail" -eq 0 ] || exit 2
  exit 0
fi

rc=0
digest=""
say() { printf '  %-8s %-22s %s\n' "$1" "$2" "${3:-}"; }
step() { # name, rc, detail
  digest="${digest}$2"
  if [ "$2" -eq 0 ]; then say ok "$1" "${3:-}"; else say REFUSE "$1" "${3:-}"; rc=1; fi
}

# --- 1. the merge base resolves.
# A shallow clone answers "no common ancestor" and every scoped command below
# then measures against nothing. HANDOVER trap 11: the fiction is silent.
BASE=$(git merge-base origin/main HEAD 2>/dev/null)
if [ -z "$BASE" ]; then
  say REFUSE "merge-base" "no common ancestor with origin/main -- git fetch --unshallow origin"
  exit 2
fi
step "merge-base" 0 "$BASE"

# --- 2. the scoped gate's MODE line, printed rather than inferred.
# CLAUDE.md rule 1: `MODE: SCOPED -- 0 script(s) run` and `MODE: FULL` both
# print zero and mean opposite things. Printing it is the whole step; a seat
# that has not seen the line has not decided what to run.
MODE=$(python3 tests/closure.py select --diff "$BASE" 2>/dev/null | grep -oE 'MODE: [A-Z]+' | head -1)
step "gate mode" 0 "${MODE:-(no mode line)}"

# --- 3. the policy corpus.
node .claude/workflows/policy_lint.mjs >/tmp/prepr-policy.$$ 2>&1
step "policy_lint" $? "$(tail -2 /tmp/prepr-policy.$$ | tr '\n' ' ')"
rm -f /tmp/prepr-policy.$$

# --- 4. the wave script's branching, when the branch touched it.
if ! git diff --quiet "$BASE"...HEAD -- .claude/workflows/web-fix-wave.js; then
  node .claude/workflows/check-wave-script.mjs >/tmp/prepr-wave.$$ 2>&1
  step "wave-script" $? "$(tail -1 /tmp/prepr-wave.$$)"
  rm -f /tmp/prepr-wave.$$
else
  say skip "wave-script" "web-fix-wave.js untouched"
fi

# --- 5. VERSION, the manifest and the notes heading are untouched.
# Versions are assigned after the merge by tools/release/stamp.py. A branch that
# moves one is refused by the stamp, which is a slow way to find out.
STAMPED=$(git diff --name-only "$BASE"...HEAD -- VERSION \
  custom_components/heatpump_optimizer/manifest.json | tr '\n' ' ')
NOTES=$(git diff "$BASE"...HEAD -- RELEASE_NOTES.md | grep -cE '^[-+]## ' || true)
if [ -n "${STAMPED// /}" ] || [ "$NOTES" -gt 0 ]; then
  step "no version edit" 1 "${STAMPED}${NOTES:+notes heading x$NOTES}"
else
  step "no version edit" 0
fi

# --- 6. claim files byte-identical to origin/main.
# A branch that claims nothing does not touch them at all, and one that does not
# touch them cannot collide with another branch's claim (#570).
CLAIMS=$(git diff --name-only origin/main...HEAD -- \
  tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt | tr '\n' ' ')
if [ -n "${CLAIMS// /}" ]; then
  say check "claim files" "$CLAIMS changed -- intended only if this branch claims drift"
else
  step "claim files" 0 "byte-identical to origin/main"
fi

# --- 7. the body, when one was passed.
BODY="${1:-}"
if [ -n "$BODY" ] && [ "$BODY" != "--self-test" ]; then
  bash tools/audit/preflight.sh < "$BODY"
  step "preflight" $?
  node .claude/workflows/policy_lint.mjs --pr-body "$BODY" --head "$(git rev-parse HEAD)" \
    --title "$(git log -1 --format=%s)" >/tmp/prepr-body.$$ 2>&1
  step "pr-body" $? "$(tail -1 /tmp/prepr-body.$$)"
  rm -f /tmp/prepr-body.$$
else
  say skip "body" "no body passed"
fi

echo
echo "PRE-PR: $(git rev-parse HEAD) $digest"
exit $rc
