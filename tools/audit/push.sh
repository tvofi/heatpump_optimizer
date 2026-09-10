#!/bin/bash
# Push a branch and give its pull request a body that has ALREADY passed the
# contract check. One command, because the ORDER is the countermeasure.
#
# WHY THIS EXISTS (#678). `## Head` names the SHA the body's evidence was
# measured at, so a body can only be written once the commit exists -- and
# nothing bound PUSHING to a body that passes. The order that works is commit,
# write the body against that SHA, check it, push. Each step was a separate
# command with its own chance to be skipped or reordered, and the shortest path
# -- push, open with a stub, repair the body after `pr-contract` goes red -- is
# the one a seat takes under time pressure. #678 carries the cost test over the
# pull requests merged on 2026-09-09; its instrument is
# `GET /commits/<head>/check-runs?check_name=pr-contract`, the listing rather
# than a pull request's check summary, which hides a red-then-green run.
#
#   tools/audit/push.sh [--write-head] [--no-pr] [--title <t>] <body.md> [issue-numbers...]
#   tools/audit/push.sh --self-test
#
# The trailing issue numbers are the ones you INTEND to close; they are handed
# to `prepr.sh`, which hands them to `preflight.sh`, which refuses a closing
# keyword that is not among them.
#
# WHAT IT GUARANTEES AND WHAT IT CANNOT. It is NOT atomic against GitHub: a
# push and a body write are two API calls and no transaction spans them. #678's
# word for step 4 is "atomically" and this script cannot deliver that, so it
# does not claim it. What it guarantees is the ORDERING -- nothing reaches the
# remote until the body has passed `tools/audit/prepr.sh` -- and that is what
# the race turns on. A seat that skips this script loses nothing it has today,
# which is the whole reason the interface is one command: a countermeasure that
# costs more than the shortest path is not used.
#
# THE TWO ARMS ARE `.claude/skills/steward/SKILL.md` S10, NOT A PREFERENCE.
# `pr-contract` reads the PULL REQUEST's head and the body as it stands when the
# run fires, so which of the push and the body write goes first decides WHICH
# COMMIT carries the one failed run:
#
#   * no pull request yet  ->  push, then create with the body. A push to a
#     branch with no pull request fires no `pull_request` event at all, so the
#     `opened` run is the first `pr-contract` run that ever exists for this
#     branch and it reads the checked body at the pushed head.
#   * a pull request exists  ->  set the body, then push. The `edited` run fires
#     against the head of that moment -- the one being abandoned -- and the
#     `synchronize` run that the push fires reads the checked body at the new
#     head. Reversing this pair is the defect: the `synchronize` run reads the
#     STALE body at the head a reviewer will read.
#
# NO GITHUB CLIENT, NO PUSH. Step 4 needs the pull-request surface, and pushing
# without being able to write the body is the defect this exists to prevent, so
# the missing-client arm refuses before the push rather than after it. A seat
# whose environment has no such binary drives the same two arms by hand; the
# mapping from those actions to the tools it does have is in
# `.claude/workflows/web-fragments.md`, which is the only file allowed to name
# them.
#
# Arguments are DATA. The three decisions this script makes -- which SHA the
# body must name, which arm to run, whether the local and the CI view of the
# `## Approval` obligation agree -- are pure functions of their inputs, so
# `--self-test` drives them from the `policy-rot` fixtures without a network, a
# remote, or a commit built for the purpose.
set -uo pipefail

# --- the pure decisions ------------------------------------------------------

head_section_sha() { # body file -> the first 7-40 hex token under `## Head`
  awk '
    /^##[[:space:]]/ { insec = ($0 ~ /^##[[:space:]]+Head[[:space:]]*$/); next }
    insec           { print }
  ' "${1:-/dev/null}" 2>/dev/null | grep -oiE '[0-9a-f]{7,40}' | head -1
}

pr_arm() { # pull-request number ('' or '-' for none) -> the arm's name
  case "${1:-}" in
    ''|-) printf 'push-then-create\n' ;;
    *)    printf 'body-then-push\n' ;;
  esac
}

# `policy_lint --pr-body` requires a `## Approval` section when the TITLE begins
# `policy:`. Locally `prepr.sh` lints against the last commit's subject; CI lints
# against the pull request's title. When `--title` makes those two disagree about
# that prefix, the local pass is not evidence about the CI run -- which is the
# same class of gap #678 is about, one artifact over. Refuse rather than warn:
# the repair is to write the commit subject the pull request is going to carry.
approval_prefix_agrees() { # title, commit subject
  local a=1 b=1
  case "${1:-}" in policy:*) a=0 ;; esac
  case "${2:-}" in policy:*) b=0 ;; esac
  [ "$a" = "$b" ]
}

# Replaces the WHOLE `## Head` section with the SHA, rather than substituting
# the hex token inside it: a section that names two SHAs has no single token to
# substitute, and #678's step 1 offers to WRITE the head, not to edit prose
# around it. Refused when the heading is absent -- a body with no `## Head` is
# `missing-section`, which the contract check refuses with a better message than
# this could -- and when the section holds a code fence, because this reader
# does not track fences and `policy_lint`'s does.
write_head() { # body file, sha
  local body="$1" sha="$2" tmp
  grep -qE '^##[[:space:]]+Head[[:space:]]*$' "$body" || return 1
  head_section_sha "$body" >/dev/null
  awk '/^##[[:space:]]/ { insec = ($0 ~ /^##[[:space:]]+Head[[:space:]]*$/); next } insec' \
    "$body" | grep -qE '^[[:space:]]*```' && return 2
  tmp="$body.push.$$"
  awk -v sha="$sha" '
    /^##[[:space:]]/ {
      if ($0 ~ /^##[[:space:]]+Head[[:space:]]*$/) { print; print ""; print "`" sha "`"; print ""; insec = 1; next }
      insec = 0
    }
    insec { next }
    { print }
  ' "$body" > "$tmp" || { rm -f "$tmp"; return 3; }
  mv "$tmp" "$body"
}

# --- self-test ---------------------------------------------------------------
# A countermeasure that cannot be shown failing does not merge
# (`.claude/rules/defect-root-cause.md`, "A detector must be shown to detect").
# This drives the decisions above against the same `policy-rot/prepr` fixtures
# `prepr.sh --self-test` uses, and pairs every refusal with the healthy input
# that must NOT be refused -- a check that fires on everything and a check that
# fires on the right thing print the same "refused" line.
#
# It does NOT drive the push or the pull-request calls: those are network, and a
# self-test that stubbed them would be asserting against its own stub. Those two
# arms are demonstrated end to end, against a throwaway branch, on the pull
# request that lands this file.
if [ "${1:-}" = "--self-test" ]; then
  cd "$(git rev-parse --show-toplevel)" || exit 2
  D=.claude/workflows/fixtures/policy-rot/prepr
  ZERO=0000000000000000000000000000000000000000
  STALE=deadbeefdeadbeefdeadbeefdeadbeefdeadbeef
  st_pass=0; st_fail=0
  st() { if [ "$1" = "$2" ]; then st_pass=$((st_pass+1)); printf '  ok   %s\n' "$3";
         else st_fail=$((st_fail+1)); printf '  FAIL %s (got %s, wanted %s)\n' "$3" "$1" "$2"; fi; }

  st "$(head_section_sha "$D/good.md")" "$ZERO" "the head section's SHA is read out of a healthy body"
  st "$(head_section_sha "$D/wrong-head.md")" "$STALE" "and out of the stale-head fixture, which is the defect's shape"
  st "$(head_section_sha "$D/no-figures.md")" "$ZERO" "a body missing a LATER section still has its head read"
  st "$(head_section_sha /dev/null)" "" "a body with no head section yields no SHA"

  st "$(pr_arm '')" "push-then-create" "no pull request: the opened run is the first pr-contract run there is"
  st "$(pr_arm '-')" "push-then-create" "an absent number reads as no pull request, not as one"
  st "$(pr_arm 704)" "body-then-push" "a pull request exists: the body is set before the push, per S10"

  approval_prefix_agrees "policy: x" "policy: x"; st $? 0 "a policy title over a policy subject agrees"
  approval_prefix_agrees "fix: x" "fix: x";       st $? 0 "a non-policy pair agrees (null control)"
  approval_prefix_agrees "policy: x" "fix: x";    st $? 1 "a policy title over a non-policy subject is refused"
  approval_prefix_agrees "fix: x" "policy: x";    st $? 1 "and the same disagreement the other way round"

  # The repair, demonstrated as a BEFORE and an AFTER against the contract check
  # itself rather than against this file's own reader. Before: the fixture is
  # refused for naming a SHA that is not the head. After: the same body, with
  # nothing else touched, passes. If `write_head` wrote nothing at all, the
  # first assertion would still pass and the second would fail -- which is the
  # direction that catches a repair that silently matched nothing.
  W=$(mktemp -d) || exit 2
  cp "$D/wrong-head.md" "$W/b.md"
  node .claude/workflows/policy_lint.mjs --pr-body "$W/b.md" --head "$ZERO" >/dev/null 2>&1
  st $? 1 "before the repair, the contract check refuses the stale head"
  write_head "$W/b.md" "$ZERO"; st $? 0 "write_head reports success on a body that has the heading"
  st "$(head_section_sha "$W/b.md")" "$ZERO" "and the section now names the head it was given"
  node .claude/workflows/policy_lint.mjs --pr-body "$W/b.md" --head "$ZERO" >/dev/null 2>&1
  st $? 0 "after the repair, the same body passes the contract check"
  # Every other section survived the rewrite: a repair that emptied the body
  # would also pass the two assertions above, because a body is refused for a
  # MISSING section only when the heading is gone, and awk dropping every line
  # would take the headings with it. Compare the two directly.
  st "$(grep -c '^## ' "$W/b.md")" "$(grep -c '^## ' "$D/wrong-head.md")" \
     "the rewrite kept every other heading (null control on the repair)"
  printf 'no head section here\n' > "$W/nohead.md"
  write_head "$W/nohead.md" "$ZERO"; st $? 1 "write_head refuses a body with no \`## Head\` heading"
  st "$(cat "$W/nohead.md")" "no head section here" "and leaves that body untouched"
  rm -rf "$W"

  printf '\n%s passed, %s failed\n' "$st_pass" "$st_fail"
  [ "$st_fail" -eq 0 ] || exit 2
  exit 0
fi

# --- arguments ---------------------------------------------------------------

WRITE_HEAD=0
NO_PR=0
TITLE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --write-head) WRITE_HEAD=1; shift ;;
    --no-pr)      NO_PR=1; shift ;;
    --title)      TITLE="${2:-}"; shift 2 ;;
    --*)          printf 'push.sh: unknown option %s\n' "$1" >&2; exit 2 ;;
    *)            break ;;
  esac
done

if [ $# -lt 1 ]; then
  sed -n '17,20p' "$0" >&2
  exit 2
fi

# Resolved before the `cd`: the body is a path the caller typed, and a caller
# who is not standing in the repository root typed a path relative to somewhere
# else. A caller's string in a shell line is #622's defect, so this is one
# expansion and no re-quoting.
BODY=$(cd "$(dirname -- "$1")" 2>/dev/null && printf '%s/%s\n' "$(pwd)" "$(basename -- "$1")")
shift
cd "$(git rev-parse --show-toplevel)" || exit 2
[ -f "$BODY" ] || { printf 'push.sh: REFUSE   no body at %s\n' "$BODY" >&2; exit 2; }

say() { printf '  %-8s %-22s %s\n' "$1" "$2" "${3:-}"; }

BR=$(git branch --show-current 2>/dev/null)
[ -n "$BR" ] || { say REFUSE "branch" "HEAD is detached, so no branch of this repository is a pull request's head"; exit 2; }
HEAD_SHA=$(git rev-parse HEAD)
SUBJECT=$(git log -1 --format=%s)
[ -n "$TITLE" ] || TITLE="$SUBJECT"

if ! approval_prefix_agrees "$TITLE" "$SUBJECT"; then
  say REFUSE "title" "\"$TITLE\" and the commit subject \"$SUBJECT\" disagree about the \`policy:\` prefix, and that prefix is what decides whether \`## Approval\` is required -- locally against the subject, in CI against the title. Write the subject the pull request will carry."
  exit 3
fi

# --- 1. the head the body names ----------------------------------------------
# The ASSERTION is not re-implemented here: `policy_lint --pr-body --head` makes
# it, `prepr.sh` calls that at `git rev-parse HEAD`, and step 2 below calls
# `prepr.sh`. Duplicating it would give a seat two checks that can disagree.
# What this step adds is #678's parenthesis -- writing the head rather than
# refusing over it -- and it runs FIRST so that the checker in step 2 reads the
# repaired body.
if [ "$WRITE_HEAD" = "1" ]; then
  WAS=$(head_section_sha "$BODY")
  write_head "$BODY" "$HEAD_SHA"
  case $? in
    0) if [ "$WAS" = "$HEAD_SHA" ]; then say ok "head" "already $(git rev-parse --short HEAD)"
       else say wrote "head" "\`## Head\` now names $(git rev-parse --short HEAD) (was ${WAS:-nothing})"; fi ;;
    1) say REFUSE "head" "no \`## Head\` heading to write into"; exit 3 ;;
    2) say REFUSE "head" "the \`## Head\` section holds a code fence; this reader does not track fences, so write the SHA by hand"; exit 3 ;;
    *) say REFUSE "head" "could not rewrite $BODY"; exit 3 ;;
  esac
fi

# --- 2. the contract check, before anything leaves this machine --------------
echo
bash tools/audit/prepr.sh "$BODY" "$@"
PREPR=$?
echo
if [ "$PREPR" -ne 0 ]; then
  say REFUSE "prepr" "the body did not pass, so NOTHING was pushed. Repair it and run this again."
  exit 3
fi
say ok "prepr" "the body passed at $(git rev-parse --short HEAD)"

# --- 3-4. which arm, then run it ---------------------------------------------
if ! command -v gh >/dev/null 2>&1; then
  say REFUSE "client" "no GitHub client on PATH, so the body cannot be written and NOTHING was pushed. Drive the arm by hand -- no pull request: push, then open it with this body; a pull request exists: set this body, then push. See .claude/workflows/web-fragments.md."
  exit 4
fi

PR=$(gh pr list --head "$BR" --state open --json number --jq '.[0].number' 2>/dev/null)
ARM=$(pr_arm "$PR")
say arm "$ARM" "${PR:+#$PR }branch $BR"

push_branch() {
  git push --set-upstream origin "$BR" || { say REFUSE "push" "git push failed"; exit 5; }
  say ok "push" "origin/$BR at $(git rev-parse --short HEAD)"
}

if [ "$NO_PR" = "1" ]; then
  # The escape exists so an interim push does not need a pull request to exist
  # first. It is refused once one does, because at that point skipping the body
  # write IS the defect: the `synchronize` run would read whatever body the
  # pull request happens to carry.
  if [ -n "$PR" ]; then
    say REFUSE "--no-pr" "#$PR is open on $BR, so a push writes its \`synchronize\` run against the body already there. Run without --no-pr."
    exit 3
  fi
  push_branch
  say note "--no-pr" "no pull request was opened; run this again without --no-pr to open one with this body"
  exit 0
fi

if [ "$ARM" = "body-then-push" ]; then
  gh pr edit "$PR" --body-file "$BODY" >/dev/null || { say REFUSE "body" "could not set #$PR's body; NOTHING was pushed"; exit 5; }
  say ok "body" "#$PR now carries this body; its \`edited\` run fires against the outgoing head"
  push_branch
  say ok "order" "the \`synchronize\` run at $(git rev-parse --short HEAD) reads the body checked above"
else
  push_branch
  URL=$(gh pr create --base main --head "$BR" --title "$TITLE" --body-file "$BODY") || {
    say REFUSE "create" "the branch is pushed and no pull request was opened -- open one with $BODY, and do not let a stub body reach it"; exit 5; }
  say ok "create" "$URL"
  say ok "order" "the \`opened\` run is the first \`pr-contract\` run on this branch and reads the body checked above"
fi

echo
echo "PUSHED: $HEAD_SHA $BR"
