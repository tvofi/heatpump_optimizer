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
#   tools/audit/prepr.sh [body.md] [intended-issue-numbers...]
#
# Self-test (used by the `pr-contract` job, and by anyone changing this file):
#
#   tools/audit/prepr.sh --self-test
#
set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 2

# --- the push-order verdict --------------------------------------------------
# WHY THIS EXISTS. Step 7 below gates `## Head` against the LOCAL head, the one
# head that is certain at the moment a body is written. `pr-contract` gates it
# against the PULL REQUEST's head, which is the remote tip. The two disagree for
# exactly as long as a commit sits unpushed, and #691 spent that window in it: at
# head b2cfbc9 a `synchronize` run passed at 19:53:33Z and the `edited` run that
# setting the body fired failed 54 seconds later -- "`## Head` does not name
# b2cfbc9, which is the head this ran on" -- because the body named the newer
# local commit. This script was green in between. The check that exists to refuse
# a stale head could not see the one staleness that reaches CI.
#
# WARN RATHER THAN REFUSE on an unpushed head, and the reason is policy, not
# taste. .claude/skills/steward/SKILL.md S10 PRESCRIBES passing through this
# state: of the two available orders it chooses "edit, then push", precisely so
# that the one refused run lands on a commit being abandoned rather than on the
# head a reviewer will read. #691 is that arm working -- head b2cfbc9 carries a
# green run at 19:53:33Z and a refused one 54 seconds later, and 99ee4b9 became
# the head. A refusal here would refuse the prescribed order, which is worse
# than the defect it answers. So the warning states the INVARIANT the two arms
# turn on -- a push must follow this body edit, or the refusal stays on your
# head -- rather than an order that contradicts the skill.
#
# What IS refused is the state no push repairs: the branch's own remote branch
# already carrying commits this head does not, where `## Head` names a SHA that
# pushing will not make current, because there is nothing to push. An autofix
# commit (S1) is exactly that shape -- S10's closing paragraph says to correct
# `## Head` after the bot pushes, and nothing checked it.
#
# THE ARM'S PREMISE IS THE RELATIONSHIP; WHAT VARIES IS WHICH REF IS COMPARED.
# A fresh local commit leaves HEAD ahead of the branch's own remote branch and
# never behind it, so on the ordinary path the refusing arm has nothing to fire
# on -- and that holds only because the compared ref is
# `refs/remotes/<remote>/<branch>`, derived from the branch's OWN name, which is
# the local mirror of `refs/heads/<branch>`, which is the pull request's head
# ref. The first version of this check read `@{u}` instead, and `@{u}` is not
# that ref: `git checkout -b foo origin/main` with `branch.autoSetupMerge` unset
# -- git's own default -- sets `branch.foo.merge = refs/heads/main`, so `@{u}`
# is `origin/main`, `behind` counts MAIN's own new commits, and the arm refused
# branches with nothing wrong with them while telling them "no push makes
# `## Head` the pull request's head" -- false there, because a push to
# `refs/heads/foo` is exactly the thing that does. The #694 review measured the
# configuration live in this repository's own clone; re-derive rather than carry
# a count, because it moves whenever a seat pushes with `-u`, and the rule is
# `git config --get branch.<name>.merge` not equal to `refs/heads/<name>`.
# `pr_head_ref` below is the repair and `main-tracking.case` pins it.
#
# NO NETWORK, EVER. The counts come from `refs/remotes/<remote>/<branch>`, a
# local mirror; nothing here fetches, because a check that hangs or fails
# offline is run with `|| true` inside a week. The cost is stated rather than
# hidden: a mirror not updated since somebody else pushed makes this too QUIET,
# never too loud -- it can report `ok` where the remote has since moved on, and
# it cannot invent an unpushed commit. A mirror that was never fetched at all is
# quiet in the same direction: the branch reads as never pushed and reaches the
# skip arm rather than a refusal. `git fetch origin "$(git branch
# --show-current)"` beforehand is what buys certainty, and the ok line names the
# ref it compared so that line is not read as CI's agreement.
#
# Arguments are DATA, not a repository: the compared ref is a function of the
# branch's name and its remote, the verdict a function of that ref's sha and the
# two counts, and of nothing else -- so --self-test drives both from fixtures
# that need no commits built and no refs written.
pr_head_ref() { # branch name ('' or '-' when detached), remote ('' or '-' -> origin)
  case "${1:-}" in ''|-) return 1 ;; esac   # a detached HEAD is nobody's head ref
  case "${2:-}" in
    ''|-) printf 'origin/%s\n' "$1" ;;
    *)    printf '%s/%s\n' "$2" "$1" ;;
  esac
}

push_order() { # own remote branch's sha ('' or '-' for none), behind, ahead
  case "${1:-}" in ''|-) return 3 ;; esac   # 3 no remote branch: nothing to compare
  if [ "${2:-0}" -gt 0 ]; then
    if [ "${3:-0}" -gt 0 ]; then return 5; fi # 5 both moved: a non-fast-forward
    return 1                                  # 1 it holds commits HEAD lacks
  fi
  if [ "${3:-0}" -gt 0 ]; then return 4; fi # 4 HEAD is not on it yet
  return 0                                  # 0 it is at this head
}

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
  # `$1` is a return code for most assertions and a ref NAME for the push-order
  # fixtures' first one, so the failure line says `got`, not `rc`.
  st() { if [ "$1" = "$2" ]; then st_pass=$((st_pass+1)); printf '  ok   %s\n' "$3";
         else st_fail=$((st_fail+1)); printf '  FAIL %s (got %s, wanted %s)\n' "$3" "$1" "$2"; fi; }

  for f in missing-section no-figures empty-section wrong-head dead-carry bad-friction backtick-bad-event bare-na folded-entry; do
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

  # The hooks check, driven over one fixture per way a wiring can be wrong.
  # `empty` and `broken` matter most: a settings file with no hooks, and one
  # that does not parse, both read exactly like a working one to anybody who
  # only looks at whether the file is there.
  for f in missing empty unreadable broken self-test-fails; do
    node .claude/workflows/policy_lint.mjs --hooks "$D/../hooks/$f.json" >/dev/null 2>&1
    st $? 1 "a settings file whose hook is $f is refused"
  done
  node .claude/workflows/policy_lint.mjs --hooks >/dev/null 2>&1
  st $? 0 "this repository's own three wired hooks pass (null control)"

  # The push-order verdict, one fixture per branch shape. Named in a list rather
  # than globbed, for the same reason the two loops above are: a glob that
  # matches nothing runs no assertions and prints the same "0 failed" a passing
  # set does. A missing file is a FAIL, not a skip.
  #
  # TWO assertions per fixture, because the #694 review found the defect in the
  # half that had none: the verdict function was right and the CALL SITE fed it
  # the wrong ref. So each fixture states which ref the shape must be compared
  # against as well as what the comparison must return, and `@{u}` is not among
  # the fields -- removing it from the input set is the repair.
  for f in detached no-upstream remote-at-head unpushed-head remote-ahead diverged main-tracking; do
    c="$D/upstream/$f.case"
    if [ ! -f "$c" ]; then st 1 0 "the $f push-order fixture is present"; continue; fi
    IFS=' ' read -r br rem up behind ahead want wantref why < <(grep -vE '^#|^[[:space:]]*$' "$c" | head -1)
    got=$(pr_head_ref "$br" "$rem") || got='-'
    st "$got" "${wantref:-?}" "${why:-$f} -- compared against ${wantref:-?}"
    push_order "$up" "$behind" "$ahead"
    st $? "${want:-?}" "${why:-$f}"
  done

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
ORDER=""
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

# --- 3a. no corpus check survives its own deletion.
# 350ms, against 1.6s for the lint pass beside it: the lane runs the acceptance
# only, never the corpus. Three checks reached main measuring nothing, so the
# cheaper detector this answers to is this one.
node .claude/workflows/policy_lint_mutants.mjs >/tmp/prepr-mutants.$$ 2>&1
step "mutants" $? "$(tail -1 /tmp/prepr-mutants.$$)"
rm -f /tmp/prepr-mutants.$$

# --- 3b. the generated Cursor rules match their source.
node .claude/workflows/rules_sync.mjs --check >/tmp/prepr-rules.$$ 2>&1
step "rules_sync" $? "$(tail -1 /tmp/prepr-rules.$$)"
rm -f /tmp/prepr-rules.$$

# --- 3c. the five copies of the shared prompt block are the canonical text.
node .claude/workflows/fragments_sync.mjs >/tmp/prepr-frag.$$ 2>&1
step "fragments" $? "$(tail -1 /tmp/prepr-frag.$$)"
rm -f /tmp/prepr-frag.$$

# --- 3d. the hooks this repository wires are present and self-testing.
node .claude/workflows/policy_lint.mjs --hooks >/tmp/prepr-hooks.$$ 2>&1
step "hooks" $? "$(tail -1 /tmp/prepr-hooks.$$)"
rm -f /tmp/prepr-hooks.$$

# --- 4. the wave script's branching, when the branch touched any of its inputs.
#
# THREE THINGS DECIDE THIS CHECK'S OUTCOME and the gate watched one of them.
# It keyed on `web-fix-wave.js`, the script under test, and so skipped itself
# on a branch whose change was to `check-wave-script.mjs` -- the checker -- and
# on one that deleted rosters, which are the population it measures. Both
# happened: the archive branch dropped three of seven rosters and this file
# printed `skip wave-script -- web-fix-wave.js untouched` while the roster
# population fell 30%, and the branch that fixed the checker was skipped by the
# gate meant to cover it. That is decisions/0004's class in a shell script: an
# assertion that is correct, that did not run, and whose run looks identical to
# one where it did. CI's `wave-script` job is unconditional, so nothing shipped
# unmeasured -- but a local gate that skips exactly when the change is in scope
# teaches a seat that the check is covered when it is not.
if ! git diff --quiet "$BASE"...HEAD -- \
     .claude/workflows/web-fix-wave.js \
     .claude/workflows/check-wave-script.mjs \
     '.claude/workflows/wave-*-groups.json'; then
  node .claude/workflows/check-wave-script.mjs >/tmp/prepr-wave.$$ 2>&1
  step "wave-script" $? "$(tail -1 /tmp/prepr-wave.$$)"
  rm -f /tmp/prepr-wave.$$
else
  say skip "wave-script" "no change to the script, the checker or the rosters"
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
  # THE INTENDED ISSUES ARE FORWARDED, and before they were, this step refused
  # every body that closed one. `preflight.sh` refuses a closing keyword whose
  # number is not in the list it was given, and this script gave it none -- so
  # `Closes #N`, which `tools/audit/briefs/fixer.md` step 7 REQUIRES of a fix
  # body, made the pre-PR gate exit non-zero with nothing wrong. CI does not
  # catch that in either direction: `pr-contract` runs the same script as
  # `preflight.sh ... || true`, so the check binds nowhere. Found by the first
  # body in twenty merges to carry a closing keyword.
  shift
  bash tools/audit/preflight.sh "$@" < "$BODY"
  step "preflight" $?
  node .claude/workflows/policy_lint.mjs --pr-body "$BODY" --head "$(git rev-parse HEAD)" \
    --title "$(git log -1 --format=%s)" >/tmp/prepr-body.$$ 2>&1
  step "pr-body" $? "$(tail -1 /tmp/prepr-body.$$)"
  rm -f /tmp/prepr-body.$$

  # --- 7a. every figure's command resolves. `pr-contract` runs the same script,
  # so this is the cheaper detector rather than a second opinion: the #715
  # defect it answers cost a review round to find, and finding it here costs one
  # node spawn on a body a seat is about to open.
  node .claude/workflows/figure_lint.mjs --pr-body "$BODY" >/tmp/prepr-fig.$$ 2>&1
  step "figures" $? "$(tail -1 /tmp/prepr-fig.$$)"
  rm -f /tmp/prepr-fig.$$

  # --- 7b. and is the head it names one the REMOTE already has? push_order above
  # carries the reasoning; this derives the branch's OWN remote branch -- the
  # local mirror of the ref a pull request's head points at -- and prints the
  # verdict. Never `@{u}`: that names whatever the branch was cut from, which on
  # git's default `git checkout -b foo origin/main` is `origin/main`.
  BR=$(git branch --show-current 2>/dev/null)
  UPREF=$(pr_head_ref "$BR" "$(git config --get "branch.$BR.remote" 2>/dev/null)") || UPREF=""
  UPSHA=""
  [ -n "$UPREF" ] && UPSHA=$(git rev-parse --verify --quiet "refs/remotes/$UPREF")
  BEHIND=0; AHEAD=0
  if [ -n "$UPSHA" ]; then
    read -r BEHIND AHEAD < <(git rev-list --left-right --count "$UPSHA...HEAD" 2>/dev/null)
    BEHIND=${BEHIND:-0}; AHEAD=${AHEAD:-0}
  fi
  push_order "$UPSHA" "$BEHIND" "$AHEAD"
  case $? in
    0) step "push order" 0 "$UPREF is at $(git rev-parse --short HEAD) -- local mirror, unfetched" ;;
    3) if [ -z "$UPREF" ]; then
         say skip "push order" "HEAD is detached, so no branch of this repository is the pull request's head"
       else
         say skip "push order" "no $UPREF yet; the push creates it, so pass $BODY to --body-file after it"
       fi ;;
    4) ORDER="HEAD is $AHEAD commit(s) ahead of $UPREF"
       say WARN "push order" "$ORDER -- A PUSH MUST FOLLOW THIS BODY EDIT" ;;
    1) step "push order" 1 "$UPREF -- this branch's own remote branch, which is the pull request's head ref -- holds $BEHIND commit(s) HEAD does not, so no push makes \`## Head\` the pull request's head -- merge $UPREF, then rewrite it" ;;
    5) step "push order" 1 "$UPREF and HEAD have diverged, $BEHIND commit(s) there against $AHEAD here: the push is refused as a non-fast-forward and the force-push past it is forbidden -- merge $UPREF, then rewrite \`## Head\` at the merge commit" ;;
    *) step "push order" 1 "$UPREF: unknown push-order verdict" ;;
  esac
else
  say skip "body" "no body passed"
fi

if [ -n "$ORDER" ]; then
  printf '\n  !!! %s, so `pr-contract` -- which reads\n' "$ORDER"
  printf '  !!! the PULL REQUEST head, not this one -- refuses this body on any run that\n'
  printf '  !!! fires before the push, the `edited` run setting it fires included.\n'
  printf '  !!! steward S10 ACCEPTS that on one condition: the push follows immediately, so\n'
  printf '  !!! the refusal lands on a commit you abandon. #691 head b2cfbc9 is that pair --\n'
  printf '  !!! green 19:53:33Z, refused 54s later, and 99ee4b9 became the head.\n'
  printf '  !!! If setting the body is your LAST action, the refusal stays on your head.\n'
fi

echo
echo "PRE-PR: $(git rev-parse HEAD) $digest"
exit $rc
