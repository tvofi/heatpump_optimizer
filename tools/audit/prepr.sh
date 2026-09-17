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

# Step 7a's whole body, so `--self-test` drives the code the step runs rather
# than a second copy of the command. A step wired into the run and demonstrated
# by a sibling command is a step nothing pins: the assertion passes while the
# call site names the wrong file, or no longer exists.
figures_check() { # body file
  node .claude/workflows/figure_lint.mjs --pr-body "$1"
}

# Step 7's body check, and the path list the `## Approval` gate is keyed on.
# Same argument as `figures_check` above: the step calls these, so `--self-test`
# drives the code the step runs rather than a second copy of the command.
#
# WHY THE PATHS ARE PASSED AT ALL. `checkPrBody` requires a `## Approval`
# heading when the change is a policy change, and since R3-D11-03 that is keyed
# on the DIFF, not on the title -- a title is written by the same seat the
# section exists to constrain, so a one-word title change switched the
# requirement off. `pr-contract` passes `--paths-file`; this script passed
# `--pr-body`, `--head` and `--title` and nothing else, so `policyPaths` was
# empty on every branch and the requirement could not fire here at all. That is
# not a check that disagreed with CI: it is a check that reported `ok` on the
# one question it had no input for. #1053 is the cost -- the body passed this
# script, the push went out, and `pr-contract` refused it with "no `## Approval`
# section, and this diff touches `docs/HANDOVER.md`".
#
# THREE-DOT, AND `--no-renames`, FOR CI'S OWN TWO REASONS. `$BASE` is the merge
# base, so `"$BASE"...HEAD` names what the BRANCH changed; a two-dot diff
# against `origin/main` attributes main's own newer commits to the branch and
# would demand `## Approval` for a policy file the branch never touched. And a
# rename is reported by its DESTINATION only, so `--no-renames` is what keeps
# moving `CLAUDE.md` to `RENAMED.md` inside the gate rather than outside it.
#
# FAIL CLOSED, AND THE LOAD-BEARING KEY IS THE RETURN CODE. A range that does
# not resolve makes this return non-zero and the caller refuses instead of
# running the check: `policy_lint.mjs` refuses an empty `--paths-file` for the
# same reason, because an empty list reads as "touches no policy file", which is
# the fail-open the keying exists to close. A seat in a shallow clone must not be
# told its body is clean when nothing looked.
#
# THE ABSENCE OF THE FILE IS THE SECOND KEY, and it is deliberate rather than
# incidental. Writing straight to `$2` would truncate it before `git` ran, so a
# failed derivation left a 0-BYTE FILE behind -- measured at rc=128 with the file
# present, by the #1054 review. Nothing in this script keyed on the file, so that
# was harmless the day it was written and exactly the shape that stops being
# harmless later: a caller added afterwards, reading the list because it is
# there, would satisfy every assertion below while reading an empty diff as
# "touches no policy file". Writing through `.part` and renaming only on success
# makes both keys agree. If a later edit drops the rename, the return code is
# still the one a caller must read.
#
# THE CLEANUP IS UNCONDITIONAL, AND THAT IS THE #1054 REVIEW'S FINDING. The
# first form cleaned up only on the redirect's failure, so a failing `mv` left
# `.part` behind -- and the caller's cleanup names `$2`, not `$2.part`, so
# nothing removed it. 138 bytes, on a path that needs `mv` to fail. Removing it
# here rather than adding a word to the caller is the point: the function owns
# the temp file it invents, under every outcome, and no caller has to know the
# name exists. `rm` runs after `$?` is captured so it cannot overwrite the
# status being returned.
diff_paths() { # merge base, out file
  local rc
  git diff --no-renames --name-only "$1"...HEAD > "$2.part" 2>/dev/null \
    && mv -f "$2.part" "$2"
  rc=$?
  rm -f "$2.part"
  return "$rc"
}

body_check() { # body file, head sha, title, paths file
  node .claude/workflows/policy_lint.mjs --pr-body "$1" --head "$2" \
    --title "$3" --paths-file "$4"
}

# A BODY IN A SHARED ROOT IS ANOTHER SEAT'S BODY WAITING TO HAPPEN. Seats of one
# session are all told the same scratchpad, and a machine has one `/tmp`, so a
# `body.md` written directly in either is overwritten by the next seat that picks
# the obvious name -- five destroyed files and one pattern kill on 2026-09-16/17,
# in the root-cause comment on #201 for the pull request that added this.
#
# SCOPE: a directory handed to more than one seat -- a `scratchpad`, its
# `claude-<uid>` parent, the system temp roots, `$TMPDIR` and `$HOME`. A worktree
# root is out of it: a worktree is one seat's by contract. The FILE is resolved
# first, so a link in a seat's own directory pointing at a shared root refuses.
# Plain `mktemp` names a unique file directly in `$TMPDIR` and is refused too:
# deliberately, since telling a unique name from a chosen one is guessing, and
# `mktemp -d` costs two characters. `<abs-scratch>/<seat>/body.md` passes.
shared_root() { # body path -> 0 when the file sits directly in a shared root
  local f d r
  f=$(realpath -- "$1" 2>/dev/null) || f=$1
  d=$(cd "$(dirname -- "$f")" 2>/dev/null && pwd -P) || return 1
  case "$d" in /tmp|/private/tmp|/var/tmp|/private/var/tmp) return 0 ;; esac
  for r in "${TMPDIR:-}" "${HOME:-}"; do
    [ -n "$r" ] && [ "$d" = "$(cd "$r" 2>/dev/null && pwd -P)" ] && return 0
  done
  case "$(basename -- "$d")" in scratchpad|claude-[0-9]*) return 0 ;; esac
  return 1
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

stamp_paths() { # name-only diff over VERSION, unified diffs of manifest.json and RELEASE_NOTES.md
  # Step 5's predicate, a pure function of its inputs so --self-test can
  # drive it. Prints the stamp-shaped paths it finds, space-separated; empty
  # means the branch touched no version.
  #
  # KEYED ON THE FIELD, NOT THE FILE. CLAUDE.md rule 4 forbids touching
  # "VERSION, the manifest VERSION, or the RELEASE_NOTES.md heading"; the
  # first form of this step diffed manifest.json by NAME and so refused every
  # manifest edit, including the one that adds `quality_scale` -- a predicate
  # wider than the rule it enforced, found by the first branch that made a
  # legitimate non-version manifest edit. The manifest's other keys are
  # ordinary production state; only its `version` line is the stamp's.
  local out=""
  if [ -n "${1// /}" ]; then out="VERSION"; fi
  if printf '%s\n' "$2" | grep -qE '^[-+][[:space:]]*"version"[[:space:]]*:'; then
    out="${out:+$out }custom_components/heatpump_optimizer/manifest.json(version)"
  fi
  # The notes: a `## ` line added or removed is a release heading, which only
  # the stamp writes. `### ` subsections do not match, because the pattern
  # needs the space straight after two hashes.
  if printf '%s\n' "${3:-}" | grep -qE '^[-+]## '; then
    out="${out:+$out }RELEASE_NOTES.md(heading)"
  fi
  printf '%s' "$out"
}

# Step 5's whole body, and the one command `pr-contract` runs for it, so CLAUDE.md
# rule 4 is refused by CI rather than only by a seat that remembered to run this
# script. Before this, the step ran locally and nowhere else: `pr-contract` ran
# `--self-test`, which drives `stamp_paths` over strings and never reads a diff,
# so a pull request bumping VERSION was refused by no check at all.
#
# THREE-DOT, FROM THE MAIN REF, NOT FROM A MERGE BASE A CALLER COMPUTED. `git diff
# A...B` takes the merge base itself, so a main that has stamped since the branch
# forked contributes nothing -- the stamp is main's commit, not the branch's. The
# argument is the main ref precisely so that `...` is load-bearing: handed a
# precomputed merge base, two dots and three would print the same diff, and a
# regression to two dots would pass every fixture. The moved-main fixture in
# --self-test is the arm that refuses two dots.
#
# FAIL CLOSED: a range that does not resolve returns 2, never an empty list,
# because an empty list is this function's all-clear.
#
# THE DIFF IS FORCED TEXTUAL, because two of the three matchers read diff BODY
# and the branch under test owns the attributes that decide whether a body is
# printed at all. `.gitattributes` is a tracked file, so a pull request adds
# `custom_components/heatpump_optimizer/manifest.json -diff` in the same commit
# that bumps the version, and `git diff` prints `Binary files a/... and b/...
# differ` with no `+  "version":` line anywhere -- `stamp_paths` then finds
# nothing and this function returns its all-clear. `--text` overrides the
# attribute and restores the hunks; `--no-textconv` covers the other half of the
# same surface, a `diff=<driver>` attribute whose driver has a textconv, so the
# matchers read the blob rather than a rendering of it. Neither flag changes
# what an ordinary diff prints, which is the null control in --self-test.
# `--name-only` is not attribute-sensitive -- VERSION cannot be hidden this way,
# and `tests/entities.py` pins the manifest version to VERSION besides -- but
# the flags are passed on all three so no later edit has to re-derive which
# call reads a body.
version_edit() { # main ref, head -> prints the stamp-owned items the range moved
  local names manifest notes out
  git rev-parse --verify --quiet "$1^{commit}" >/dev/null || return 2
  git rev-parse --verify --quiet "$2^{commit}" >/dev/null || return 2
  names=$(git diff --text --no-textconv --name-only "$1...$2" -- VERSION 2>/dev/null) || return 2
  manifest=$(git diff --text --no-textconv "$1...$2" -- custom_components/heatpump_optimizer/manifest.json 2>/dev/null) || return 2
  notes=$(git diff --text --no-textconv "$1...$2" -- RELEASE_NOTES.md 2>/dev/null) || return 2
  out=$(stamp_paths "$names" "$manifest" "$notes")
  printf '%s' "$out"
  [ -z "$out" ]
}

# `pr-contract`'s entry point: `prepr.sh --version-edit <main ref> <head>`. It
# exits before anything below, which needs a body, node and the closures.
if [ "${1:-}" = "--version-edit" ]; then
  found=$(version_edit "${2:-}" "${3:-}"); ve=$?
  case $ve in
    0) printf 'no version edit: %s...%s moves none of VERSION, the manifest version or a notes heading\n' "${2:-}" "${3:-}" ;;
    1) printf 'REFUSE no version edit: %s...%s moves %s\n' "${2:-}" "${3:-}" "$found"
       printf 'CLAUDE.md rule 4: versions are assigned after the merge by tools/release/stamp.py; restore these to the merge base.\n' ;;
    *) printf 'REFUSE no version edit: %s...%s did not resolve, so nothing was compared -- fetch the main ref and full history\n' "${2:-}" "${3:-}" ;;
  esac
  exit "$ve"
fi

# --- self-test ---------------------------------------------------------------
# A check that cannot be shown failing does not merge. This drives the two steps
# that are pure functions of their input -- the body checks -- against the rot
# fixtures, and asserts the healthy one stays silent. The branch-shape steps
# (merge base, gate mode, version edit, claim files) are demonstrated by the
# `pr-contract` job running this script on every pull request.
if [ "${1:-}" = "--self-test" ]; then
  D=.claude/workflows/fixtures/policy-rot/prepr
  ZERO=0000000000000000000000000000000000000000
  # A base that DOES resolve, for the success arm below. HEAD always resolves
  # and needs no remote, so this arm runs in a clone with no `origin` too.
  BASE_ST=HEAD
  st_pass=0; st_fail=0
  # `$1` is a return code for most assertions and a ref NAME for the push-order
  # fixtures' first one, so the failure line says `got`, not `rc`.
  st() { if [ "$1" = "$2" ]; then st_pass=$((st_pass+1)); printf '  ok   %s\n' "$3";
         else st_fail=$((st_fail+1)); printf '  FAIL %s (got %s, wanted %s)\n' "$3" "$1" "$2"; fi; }

  for f in missing-section no-figures empty-section wrong-head dead-carry bad-friction backtick-bad-event bare-na folded-entry bullet-after-entry; do
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

  # Step 7a, driven through `figures_check` -- the function the step calls, so
  # a call site that stops calling it fails here. The rot fixture is the #715
  # defect itself, `--arg` passed to `gh api`; the null control is the same
  # fixture set's healthy body, whose figure names an in-tree instrument.
  # The exit status alone does not pin WHICH instrument the step runs: another
  # body check refuses the same rot fixture and passes the same healthy one, so
  # a `figures_check` rewired to it would satisfy a status-only assertion. Each
  # arm therefore also reads a string only this instrument prints.
  figures_check .claude/workflows/fixtures/figures/gh-arg.md >/tmp/prepr-figst.$$ 2>&1
  st $? 1 "a body whose figure command cannot resolve is refused"
  grep -q -- 'has no `--arg` flag' /tmp/prepr-figst.$$
  st $? 0 "and the step's own output names the flag, so the step runs the figure check"
  figures_check "$D/good.md" >/tmp/prepr-figst.$$ 2>&1
  st $? 0 "a body whose figure command resolves is silent (null control)"
  grep -q '0 refused' /tmp/prepr-figst.$$
  st $? 0 "and it reached a verdict rather than examining nothing (null control)"
  rm -f /tmp/prepr-figst.$$

  # Step 7's body check, driven through `body_check` -- the function the step
  # calls -- over ONE body and three path lists. One arm alone would pin a check
  # that always fires or never does, and "never does" is the state this script
  # shipped in: with no `--paths-file`, `policyPaths` was empty, `## Approval`
  # could not be required, and every branch read `ok pr-body`.
  #
  # `needs-approval.md` is the fixture for both directions because it differs
  # from the healthy body in exactly one thing -- no `## Approval` -- so the
  # only variable across these arms is the diff.
  #
  # THE NON-POLICY ARM IS THE CONTROL THAT MATTERS MORE. Over-firing here would
  # refuse every ordinary pull request in this repository, and a refusal that
  # fires on everything pins nothing. The exit status alone does not pin WHICH
  # refusal fired -- this body is refusable on other grounds by other flags -- so
  # the policy arm also reads the approval gate's own sentence.
  body_check "$D/needs-approval.md" "$ZERO" '' "$D/paths-real.txt" >/tmp/prepr-bodyst.$$ 2>&1
  st $? 1 "a body with no \`## Approval\` is refused when the diff touches a policy path"
  grep -q 'no `## Approval` section' /tmp/prepr-bodyst.$$
  st $? 0 "and the refusal is the approval gate's own, so the paths reached the check"
  body_check "$D/needs-approval.md" "$ZERO" '' "$D/paths-nonpolicy.txt" >/dev/null 2>&1
  st $? 0 "the same body is silent when the diff touches no policy path (null control)"
  body_check "$D/needs-approval.md" "$ZERO" '' "$D/paths-empty.txt" >/dev/null 2>&1
  st $? 1 "a path list that derived nothing is refused, not read as \"touches no policy file\""
  rm -f /tmp/prepr-bodyst.$$

  # The degraded arm, asserted on BOTH keys because the first version of it
  # asserted a property the code did not have. A range that does not resolve must
  # make the DERIVATION fail, so the step refuses rather than handing the check a
  # list nothing wrote -- and it must leave no list behind either, so a caller
  # added later that reads the file rather than the status fails closed as well.
  # `git diff` exits 128 on an unknown revision, not 1, so the first assertion is
  # on the branch taken rather than on the number.
  rm -f /tmp/prepr-bodyst.$$ /tmp/prepr-bodyst.$$.part
  if diff_paths "$ZERO" /tmp/prepr-bodyst.$$ >/dev/null 2>&1; then dp=0; else dp=1; fi
  st "$dp" 1 "a base that does not resolve makes the path derivation fail"
  if [ -e /tmp/prepr-bodyst.$$ ] || [ -e /tmp/prepr-bodyst.$$.part ]; then fp=1; else fp=0; fi
  st "$fp" 0 "and leaves no list behind, not even an empty one, so the file key fails closed too"
  rm -f /tmp/prepr-bodyst.$$ /tmp/prepr-bodyst.$$.part
  # The SUCCESS path's own temp-file assertion, which nothing pinned before: a
  # derivation that works must also leave no `.part` behind.
  #
  # WHAT IT DOES NOT PIN, measured rather than assumed. A first version of this
  # comment claimed the arm would catch a later edit replacing `mv` with `cp`.
  # It does not: driven, `cp -f` leaves `--self-test` at 48/0, because the
  # unconditional cleanup above removes the copy's leftover too. That is the
  # fix working rather than a hole -- under either verb no `.part` survives --
  # but the arm's reach is the PROPERTY, not the verb, and saying otherwise
  # would be a claim stronger than the check that backs it.
  diff_paths "$BASE_ST" /tmp/prepr-bodyst.$$ >/dev/null 2>&1; dp=$?
  if [ -e /tmp/prepr-bodyst.$$.part ]; then fp=1; else fp=0; fi
  st "$dp" 0 "a base that resolves makes the path derivation succeed (null control)"
  st "$fp" 0 "and leaves no \`.part\` behind either, so the temp file is the function's own"
  rm -f /tmp/prepr-bodyst.$$ /tmp/prepr-bodyst.$$.part

  # THE `mv`-FAILURE ARM, and it exists because the #1054 review measured the
  # leak rather than reasoning about it: the first form cleaned up only on the
  # redirect's failure, so a failing `mv` left 138 bytes of `.part` behind and
  # the caller's `rm -f "$PATHS"` did not name it.
  #
  # The shape is buildable, which is the only reason this is an arm rather than
  # a disclosure. `$2` is an existing DIRECTORY holding a non-empty directory
  # called `<basename>.part`, so the redirect succeeds -- `$2.part` is an
  # ordinary file beside it -- and `mv` then refuses, because moving that file
  # into `$2` would have to replace a directory that is not empty. Source and
  # destination share a parent by construction, so every permission-based way of
  # failing `mv` fails the redirect first and never reaches this path; this is
  # the one route that separates them.
  MVD=$(mktemp -d)
  mkdir -p "$MVD/d/d.part/occupied"
  diff_paths "$BASE_ST" "$MVD/d" >/dev/null 2>&1; dp=$?
  if [ -e "$MVD/d.part" ]; then fp=1; else fp=0; fi
  st "$dp" 1 "a derivation whose rename fails is refused"
  st "$fp" 0 "and cleans up after itself, so a failing \`mv\` leaks no \`.part\`"
  rm -rf "$MVD"

  # Step 5, driven through `stamp_paths` -- the function the step calls. The
  # over-fire control is the arm that matters: the step shipped keyed on the
  # manifest's file name and refused every manifest edit, so the arm that pins
  # "a non-version manifest edit passes" is the one the old predicate fails.
  # The other three are the stamp's own shapes, each of which must still refuse.
  got=$(stamp_paths '' '+  "quality_scale": "platinum",')
  st "$got" '' "a manifest edit that is not the version field passes (over-fire control)"
  got=$(stamp_paths '' '-  "version": "6.5.1",
+  "version": "6.5.2",')
  st "$got" 'custom_components/heatpump_optimizer/manifest.json(version)' "a manifest version bump is refused, and named by field"
  got=$(stamp_paths 'VERSION' '')
  st "$got" 'VERSION' "a VERSION edit is refused"
  got=$(stamp_paths 'VERSION' '-  "version": "6.5.0",
+  "version": "6.5.1",
+  "quality_scale": "platinum",')
  st "$got" 'VERSION custom_components/heatpump_optimizer/manifest.json(version)' "a stamp-shaped diff is refused on both, and the added key does not mask it"
  got=$(stamp_paths '' '' '+## v6.5.2')
  st "$got" 'RELEASE_NOTES.md(heading)' "a release-notes heading is refused, and named"
  got=$(stamp_paths '' '' '+### Fixed
+- a line under an existing release')
  st "$got" '' "a notes subsection or bullet passes (over-fire control)"

  # `version_edit` over real commits, because what it adds to `stamp_paths` is
  # the RANGE, and a range is only exercised by a history. One throwaway
  # repository: `base` forks `main` and every PR shape; `main` then stamps.
  # Each refusing arm is one file matcher, so dropping any matcher fails its
  # own line; the moved-main arm is the one two dots fail, because a two-dot
  # diff reports the stamp main made after the fork as the branch's; and the
  # merged arm is the ordinary state of a branch updated with `git merge`.
  VER=$(mktemp -d)
  (
    set -e; cd "$VER"; git init -q -b main .
    git config user.name st; git config user.email st@st
    mkdir -p custom_components/heatpump_optimizer docs
    printf '6.5.1\n' > VERSION
    printf '{\n  "domain": "x",\n  "version": "6.5.1"\n}\n' > custom_components/heatpump_optimizer/manifest.json
    printf '# Notes\n\n## v6.5.1\n\n- a\n' > RELEASE_NOTES.md
    printf 'doc\n' > docs/a.md
    git add -A; git commit -qm base; git tag base
    pr() { git checkout -q -b "$1" base; shift; "$@"; git add -A; git commit -qm pr; }
    pr ver sh -c 'printf "6.5.2\n" > VERSION'
    pr man sh -c 'sed -i.bak "s/6.5.1/6.5.2/" custom_components/heatpump_optimizer/manifest.json && rm custom_components/heatpump_optimizer/manifest.json.bak'
    pr notes sh -c 'printf "# Notes\n\n## v6.5.2\n\n- b\n\n## v6.5.1\n\n- a\n" > RELEASE_NOTES.md'
    pr docs sh -c 'printf "more\n" >> docs/a.md'
    # THE BLINDED PAIR. `.gitattributes` is tracked, so the branch that bumps a
    # version owns whether its own diff has a body: `-diff` makes git print
    # `Binary files ... differ` instead of the hunks the two body matchers read.
    # Each is a separate branch so a regression on one file cannot be masked by
    # the other still refusing. `attr-only` is their null control -- the same
    # `.gitattributes` line with no version edit under it still passes, so an
    # implementation that simply refused any branch touching `.gitattributes`
    # fails here rather than reading as a fix.
    pr manattr sh -c 'sed -i.bak "s/6.5.1/6.5.2/" custom_components/heatpump_optimizer/manifest.json && rm custom_components/heatpump_optimizer/manifest.json.bak && printf "custom_components/heatpump_optimizer/manifest.json -diff\n" > .gitattributes'
    pr notesattr sh -c 'printf "# Notes\n\n## v6.5.2\n\n- b\n\n## v6.5.1\n\n- a\n" > RELEASE_NOTES.md && printf "RELEASE_NOTES.md -diff\n" > .gitattributes'
    pr attronly sh -c 'printf "custom_components/heatpump_optimizer/manifest.json -diff\nRELEASE_NOTES.md -diff\n" > .gitattributes'
    # AND THE OTHER HALF OF THE SAME SURFACE, which `--text` alone does not
    # cover. `diff=<driver>` with a `textconv` makes git diff a RENDERING of the
    # blob rather than the blob, and `--text` does not override it -- only
    # `--no-textconv` does. A driver whose textconv prints nothing therefore
    # produces a diff with no body at all, on a file git never called binary, so
    # the two body matchers read an empty string and the function returns its
    # all-clear. Without these arms `--no-textconv` is unpinned: dropping that
    # one flag passed every other check in this file while reopening the vector.
    # The driver is repo-local config, which is the shape a contributor controls
    # (`.git/config` is not tracked, but a `diff=` attribute IS, and a seat or a
    # runner that has ever set up a driver by that name supplies the other half).
    git config diff.blind.textconv true
    pr mantc sh -c 'sed -i.bak "s/6.5.1/6.5.2/" custom_components/heatpump_optimizer/manifest.json && rm custom_components/heatpump_optimizer/manifest.json.bak && printf "custom_components/heatpump_optimizer/manifest.json diff=blind\n" > .gitattributes'
    pr notestc sh -c 'printf "# Notes\n\n## v6.5.2\n\n- b\n\n## v6.5.1\n\n- a\n" > RELEASE_NOTES.md && printf "RELEASE_NOTES.md diff=blind\n" > .gitattributes'
    pr tconly sh -c 'printf "custom_components/heatpump_optimizer/manifest.json diff=blind\nRELEASE_NOTES.md diff=blind\n" > .gitattributes'
    git checkout -q main
    printf '6.5.2\n' > VERSION
    sed -i.bak 's/6.5.1/6.5.2/' custom_components/heatpump_optimizer/manifest.json && rm custom_components/heatpump_optimizer/manifest.json.bak
    printf '# Notes\n\n## v6.5.2\n\n- b\n\n## v6.5.1\n\n- a\n' > RELEASE_NOTES.md
    git commit -qam 'v6.5.2 stamp'
    git checkout -q -b merged docs; git merge -q --no-edit main
  ) >/dev/null 2>&1
  ve() { (cd "$VER" && version_edit "$@"); }
  # THE ATTRIBUTE ARMS NEED THE BRANCH CHECKED OUT, and that is not a fixture
  # convenience -- it is the shape CI runs in. `git diff` resolves attributes
  # from the WORKING TREE, not from the commits in the range, so a branch's own
  # `.gitattributes` only takes effect once that branch is what is checked out.
  # `pr-contract` checks the pull request out and then runs `--version-edit`, so
  # the branch's line is live there. Diffing the same two commits from a
  # different checkout -- which is what the arms above do -- reads the hunks
  # whatever the branch declared, and would have passed with no fix at all.
  veco() { (cd "$VER" && git checkout -q "$2" && version_edit "$@"); }
  got=$(ve base ver); st "$?:$got" '1:VERSION' "a pull request editing VERSION is refused"
  got=$(ve base man); st "$?:$got" '1:custom_components/heatpump_optimizer/manifest.json(version)' "a pull request editing the manifest version is refused"
  got=$(ve base notes); st "$?:$got" '1:RELEASE_NOTES.md(heading)' "a pull request adding a notes heading is refused"
  got=$(veco base manattr); st "$?:$got" '1:custom_components/heatpump_optimizer/manifest.json(version)' "a manifest version edit hidden by a .gitattributes -diff line is still refused"
  got=$(veco base notesattr); st "$?:$got" '1:RELEASE_NOTES.md(heading)' "a notes heading hidden by a .gitattributes -diff line is still refused"
  got=$(veco base attronly); st "$?:$got" '0:' "a .gitattributes-only pull request passes (over-fire control for the two arms above)"
  got=$(veco base mantc); st "$?:$got" '1:custom_components/heatpump_optimizer/manifest.json(version)' "a manifest version edit hidden by a diff=<driver> textconv is still refused"
  got=$(veco base notestc); st "$?:$got" '1:RELEASE_NOTES.md(heading)' "a notes heading hidden by a diff=<driver> textconv is still refused"
  got=$(veco base tconly); st "$?:$got" '0:' "a diff=<driver> line with no version edit under it passes (over-fire control for the two arms above)"
  (cd "$VER" && git checkout -q main)
  got=$(ve base docs); st "$?:$got" '0:' "a docs-only pull request passes (null control)"
  got=$(ve main docs); st "$?:$got" '0:' "a pull request whose main has stamped since it forked passes (the arm two dots fail)"
  got=$(ve main merged); st "$?:$got" '0:' "a pull request that merged a stamped main passes (null control)"
  got=$(ve no-such-ref docs); st "$?:$got" '2:' "a main ref that does not resolve is refused, not read as no edit"
  # The call site `pr-contract` runs, not only the function.
  out=$(cd "$VER" && bash "$OLDPWD/tools/audit/prepr.sh" --version-edit base ver 2>&1); st $? 1 "--version-edit exits non-zero on a VERSION edit"
  case "$out" in *"REFUSE no version edit"*VERSION*) st 1 1 "and names what it refused";; *) st 0 1 "and names what it refused";; esac
  (cd "$VER" && bash "$OLDPWD/tools/audit/prepr.sh" --version-edit main merged >/dev/null 2>&1); st $? 0 "--version-edit exits zero on a merged, stamped main (null control)"
  rm -rf "$VER"

  # The shared-root refusal, over real directories because the predicate resolves
  # them. The defect's two shapes refuse; a seat's own subdirectory and a bare
  # `mktemp -d` pass, so a predicate refusing every temp path fails here.
  SRD=$(mktemp -d); mkdir -p "$SRD/scratchpad/seat" "$SRD/t" "$SRD/h" "$SRD/claude-501"
  shared_root "$SRD/scratchpad/body.md"; st $? 0 "a body directly in a scratchpad is refused"
  shared_root /tmp/body.md; st $? 0 "a body directly in /tmp is refused"
  TMPDIR="$SRD/t" shared_root "$SRD/t/body.md"; st $? 0 "a body directly in \$TMPDIR is refused"
  MKF=$(mktemp); shared_root "$MKF"; st $? 0 "a plain mktemp file is refused (the stated choice)"; rm -f "$MKF"
  HOME="$SRD/h" shared_root "$SRD/h/body.md"; st $? 0 "a body directly in \$HOME is refused"
  shared_root "$SRD/claude-501/body.md"; st $? 0 "a body directly in a claude-<uid> root is refused"
  : > "$SRD/scratchpad/real.md"; ln -s "$SRD/scratchpad/real.md" "$SRD/scratchpad/seat/link.md"
  shared_root "$SRD/scratchpad/seat/link.md"; st $? 0 "a link in a seat directory to a root file is refused"
  : > "$SRD/scratchpad/seat/real.md"; ln -s "$SRD/scratchpad/seat/real.md" "$SRD/h/link.md"
  shared_root "$SRD/h/link.md"; st $? 1 "a link to a seat-directory file passes (null control)"
  shared_root "$SRD/scratchpad/seat/body.md"; st $? 1 "a body in the seat's own subdirectory passes (null control)"
  shared_root "$SRD/body.md"; st $? 1 "a body in a mktemp -d directory passes (null control)"
  # The call site, not only the function: the run stops after the body-path step.
  out=$(PREPR_BODY_PATH_ONLY=1 bash tools/audit/prepr.sh "$SRD/scratchpad/body.md" 2>&1); st $? 2 "prepr.sh refuses a root body at its call site"
  case "$out" in *"REFUSE   body path"*) st 1 1 "and names the step";; *) st 0 1 "and names the step";; esac
  out=$(PREPR_BODY_PATH_ONLY=1 bash tools/audit/prepr.sh "$SRD/scratchpad/seat/body.md" 2>&1); st $? 0 "and passes a seat body there (null control)"
  case "$out" in *"ok       body path"*) st 1 1 "printing an ok line, so a skipped step is visible";; *) st 0 1 "printing an ok line, so a skipped step is visible";; esac
  rm -rf "$SRD"

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

# --- 0. the body is not in a root other seats write to (`shared_root` above).
# First, and fatal: every later step would read a file another seat may rewrite.
if [ -n "${1:-}" ]; then
  if shared_root "$1"; then
    say REFUSE "body path" "$1 sits directly in a root other seats write to -- move it to your own subdirectory, e.g. <abs-scratch>/<seat>/"
    exit 2
  fi
  say ok "body path" "not directly in a shared root"
  [ -z "${PREPR_BODY_PATH_ONLY:-}" ] || exit 0
fi

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
# THE BRIEFS ARE A FOURTH INPUT, and the same shape repeated once more (#1062):
# the checker parses every backticked verdict example out of tools/audit/briefs/
# against VERDICT_RE, so a briefs-only branch that shortened one example was
# printed `skip` here and went red on CI's unconditional job.
if ! git diff --quiet "$BASE"...HEAD -- \
     .claude/workflows/web-fix-wave.js \
     .claude/workflows/check-wave-script.mjs \
     '.claude/workflows/wave-*-groups.json' \
     'tools/audit/briefs/*.md'; then
  node .claude/workflows/check-wave-script.mjs >/tmp/prepr-wave.$$ 2>&1
  step "wave-script" $? "$(tail -1 /tmp/prepr-wave.$$)"
  rm -f /tmp/prepr-wave.$$
else
  say skip "wave-script" "no change to the script, the checker, the rosters or the briefs"
fi

# --- 5. VERSION, the manifest and the notes heading are untouched.
# Versions are assigned after the merge by tools/release/stamp.py. A branch that
# moves one is refused by the stamp, which is a slow way to find out.
# `version_edit` is also what `pr-contract` runs, through --version-edit above,
# so this is the cheaper detector for the same refusal rather than a second one.
STAMPED=$(version_edit origin/main HEAD)
step "no version edit" $? "$STAMPED"

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
  # THE PATHS ARE THE SECOND INPUT, and until #1053 this step had only the
  # first. `diff_paths` above carries why they are derived three-dot and with
  # `--no-renames`, and why a derivation that fails refuses here rather than
  # letting the check run against a list nothing wrote. `pr-contract` runs the
  # same node script with the same two inputs, so this stays the cheaper
  # detector rather than a second opinion.
  PATHS=/tmp/prepr-paths.$$
  if diff_paths "$BASE" "$PATHS"; then
    body_check "$BODY" "$(git rev-parse HEAD)" "$(git log -1 --format=%s)" "$PATHS" \
      >/tmp/prepr-body.$$ 2>&1
    step "pr-body" $? "$(tail -1 /tmp/prepr-body.$$)"
    rm -f /tmp/prepr-body.$$
  else
    step "pr-body" 1 "the changed-path list did not derive from $BASE...HEAD, so the \`## Approval\` gate was not run -- an empty list reads as \"touches no policy file\", which is the fail-open it exists to close"
  fi
  rm -f "$PATHS"

  # --- 7a. every figure's command resolves. `pr-contract` runs the same script,
  # so this is the cheaper detector rather than a second opinion: the #715
  # defect it answers cost a review round to find, and finding it here costs one
  # node spawn on a body a seat is about to open.
  figures_check "$BODY" >/tmp/prepr-fig.$$ 2>&1
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
