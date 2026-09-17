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
#   * the query did not answer  ->  refuse, before the push. Which arm is right
#     is not knowable, and the arm that guesses is the one that pushes.
#
# NO ANSWER, NO PUSH -- and a client on `PATH` is not an answer. Step 4 needs the
# pull-request surface, and pushing without being able to write the body is the
# defect this exists to prevent, so the missing-client arm refuses before the
# push rather than after it, and the QUERY arm refuses the same way. A seat
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

# THE QUERY HAS THREE OUTCOMES, NOT TWO, and the third is a refusal. A pull
# request exists; none exists; or the query did not answer. Reading the first
# two out of an empty string -- which is what a discarded stderr and an unread
# exit status leave behind -- makes "I could not ask" answer `push-then-create`,
# so the branch reaches the remote while an open pull request keeps its stale
# body. That is the defect this whole script exists to prevent, reached through
# the script itself; a fix review returned `blocked` on exactly it.
#
# READING THE EXIT STATUS IS NECESSARY AND NOT SUFFICIENT, which is why the arm
# is decided from the listing TEXT and not from an absence of error. Measured on
# gh 2.98.0 against this repository:
#
#   gh pr list --head <a branch with an open PR> --state open \
#              --json number --jq '.[0].nosuch'     ->  rc 0, stdout ''
#   gh pr list --head <a branch with no PR>    --state open \
#              --json number --jq '.[0].number'     ->  rc 0, stdout ''
#
# byte-identical, both succeeding. So a filter that is silently wrong about the
# schema -- a renamed field, a typo -- is indistinguishable from "no pull
# request" even to a caller that reads the status. The filter is therefore gone
# and the whole listing is classified: `[]` is a POSITIVE statement that none is
# open, an array naming a number names one, and anything else is `unknown`.
pr_from_listing() { # query rc, listing text -> a pull-request number, 'none', 'unknown'
  local txt n
  [ "${1:-1}" = "0" ] || { printf 'unknown\n'; return 0; }
  txt=$(printf '%s' "${2:-}" | tr -d '[:space:]')
  case "$txt" in
    '[]')    printf 'none\n'; return 0 ;;
    '['*']') ;;
    *)       printf 'unknown\n'; return 0 ;;
  esac
  n=$(printf '%s' "$txt" | grep -oE '"number":[0-9]+' | head -1 | grep -oE '[0-9]+')
  if [ -n "$n" ]; then printf '%s\n' "$n"; else printf 'unknown\n'; fi
}

# FAIL-CLOSED BY CONSTRUCTION. Only the literal `none` selects the push arm and
# only an all-digit number selects the body arm; every other string -- `unknown`,
# the empty string, a word, a sentinel a later edit invents -- refuses. Written
# this way round so that a caller which stops classifying, or a new caller that
# never started, cannot fall through to a push.
pr_arm() { # pr_from_listing's answer -> the arm's name
  case "${1:-}" in
    none)        printf 'push-then-create\n' ;;
    ''|*[!0-9]*) printf 'refuse\n' ;;
    *)           printf 'body-then-push\n' ;;
  esac
}

# `policy_lint --pr-body` requires a `## Approval` section on EITHER of two
# keys, and this warning is about one of them. The DIFF touching a
# `POLICY_GLOBS` path is the first, and since `prepr.sh` was given
# `--paths-file` both sides derive it the same way from the same merge base, so
# there is nothing left to disagree about there. The TITLE beginning `policy:`
# is the second, and it is still asymmetric: locally `prepr.sh` lints against
# the last commit's SUBJECT, CI against the pull request's TITLE. When those two
# disagree about that prefix, the local pass is not evidence about the CI run --
# the same class of gap #678 is about, one artifact over.
#
# WARN RATHER THAN REFUSE, on `prepr.sh`'s own push-order precedent. The two
# disagree for an ordinary and correct reason as well as a wrong one: `git merge
# origin/main` makes the last subject a merge commit's, and every policy branch
# that updates itself from main before pushing then has a subject no pull request
# title will ever equal. A refusal there refuses the prescribed order, and a
# check that blocks the legitimate path is a check a seat routes around --
# which is the failure mode this whole script is written against. So it states
# the invariant and leaves the seat to act on it.
approval_prefix_agrees() { # title, commit subject
  local a=1 b=1
  case "${1:-}" in policy:*) a=0 ;; esac
  case "${2:-}" in policy:*) b=0 ;; esac
  [ "$a" = "$b" ]
}

# Does a declared SHA name a given commit? Either may be an abbreviation, so the
# comparison is a prefix in both directions rather than equality -- `dcea170`
# and its 40-character form are the same head, and treating them as different
# rewrites a body that was already right.
sha_names() { # declared token, sha -> 0 when the token names that commit
  local a b
  a=$(printf '%s' "${1:-}" | tr 'A-Z' 'a-z')
  b=$(printf '%s' "${2:-}" | tr 'A-Z' 'a-z')
  [ -n "$a" ] && [ -n "$b" ] || return 1
  case "$b" in "$a"*) return 0 ;; esac
  case "$a" in "$b"*) return 0 ;; esac
  return 1
}

# Does the `## Head` section still NAME a SHA, by the contract check's own rule?
# `checkPrBody` tests `headSec.includes(head) || headSec.includes(head.slice(0,
# 7))`, so this mirrors that substring rather than inventing a second rule the
# two could disagree about.
head_section_names() { # body file, sha
  local pfx
  pfx=$(printf '%s' "${2:-}" | cut -c1-7)
  [ -n "$pfx" ] || return 1
  awk '/^##[[:space:]]/ { insec = ($0 ~ /^##[[:space:]]+Head[[:space:]]*$/); next } insec' \
    "${1:-/dev/null}" | grep -qiF "$pfx"
}

# SETS THE SHA AND LEAVES THE SECTION ALONE. It replaced the WHOLE `## Head`
# section until #715 round twelve, on the reading that a section naming two SHAs
# has no single token to substitute. That reading cost the record: `## Head` in
# this programme carries the round-by-round history beside the SHA, and the
# section's every line but the declaration went with it -- so a push through
# this script deleted the provenance the script exists to protect. It was never what the contract asked for either:
# `policy_lint --pr-body --head` tests the section with `includes`, a substring,
# so naming the SHA is sufficient and the prose may stay.
#
# WHAT IS SUBSTITUTED IS THE DECLARATION LINE, not every hex token in the
# section. A declaration line is one whose whole content, backticks and space
# stripped, is a single 7-40 hex token -- the shape every body in this programme
# writes, and the shape `head_section_sha` already reads. Prose that CITES a
# commit is a different thing and is left standing, which is the whole point.
# When the section declares no SHA at all the declaration is inserted under the
# heading instead, because there is then nothing to substitute.
#
# THE RESIDUAL IS WARNED, NOT REFUSED. If the prose also cites the superseded
# SHA it survives the substitution, and the contract check -- a substring --
# would then still be satisfied at that old head. Refusing there would refuse
# the prescribed order on a body that is doing nothing wrong, and this file's
# own `approval_prefix_agrees` already settles that trade: a check that blocks
# the legitimate path is one a seat routes around. So it states the invariant on
# stderr and leaves the seat to act on it.
#
# Refused when the heading is absent -- a body with no `## Head` is
# `missing-section`, which the contract check refuses with a better message than
# this could -- and when the section holds a code fence, because this reader
# does not track fences and `policy_lint`'s does.
write_head() { # body file, sha
  local body="$1" sha="$2" tmp was
  grep -qE '^##[[:space:]]+Head[[:space:]]*$' "$body" || return 1
  awk '/^##[[:space:]]/ { insec = ($0 ~ /^##[[:space:]]+Head[[:space:]]*$/); next } insec' \
    "$body" | grep -qE '^[[:space:]]*```' && return 2
  was=$(head_section_sha "$body")
  sha_names "$was" "$sha" && return 0
  tmp="$body.push.$$"
  # Two passes over the same file: the first finds the declaration line, the
  # second rewrites it. `{7,40}` is not used -- interval expressions are not
  # portable across the awks this runs on -- so the token is measured with
  # `length()` instead.
  awk -v sha="$sha" '
    function isdecl(l,   t) {
      t = l; gsub(/[[:space:]]/, "", t); gsub(/`/, "", t)
      return (t ~ /^[0-9a-fA-F]+$/ && length(t) >= 7 && length(t) <= 40)
    }
    FNR == 1 { insec = 0 }
    /^##[[:space:]]/ { insec = ($0 ~ /^##[[:space:]]+Head[[:space:]]*$/) }
    FNR == NR { if (insec && $0 !~ /^##[[:space:]]/ && !decl && isdecl($0)) decl = FNR; next }
    {
      if (FNR == decl) { print "`" sha "`"; next }
      if (pend) { pend = 0; if ($0 !~ /^[[:space:]]*$/) print "" }
      print
      if (!decl && $0 ~ /^##[[:space:]]+Head[[:space:]]*$/) { print ""; print "`" sha "`"; pend = 1 }
    }
  ' "$body" "$body" > "$tmp" || { rm -f "$tmp"; return 3; }
  mv "$tmp" "$body" || return 3
  if [ -n "$was" ] && head_section_names "$body" "$was"; then
    printf 'push.sh: WARN     `## Head` still names the superseded %s in its prose, so the contract check -- a substring -- is satisfied at that old head too. Left as written, because it is the record; edit it by hand if the sentence is not history.\n' \
      "$(printf '%s' "$was" | cut -c1-7)" >&2
  fi
  return 0
}

# THE BODY IS WRITTEN OVER REST, NOT `gh pr edit`. Since decision 0009 step 3 a
# seat authors as a machine account whose token carries `repo` and `workflow`
# only, and `gh pr edit` fetches the pull request over GraphQL with fields that
# require `read:org` -- so the body arm refused on every pull request that
# account opened, and the #1084, #1090, #1091 and #1098 seats each set the body
# by hand with this same PATCH. `gh pr create` and `gh pr list` were measured
# with that token and need `repo` alone, so they stay.
#
# A PATCH that returned 0 is not evidence the body landed, so the live body is
# read back and compared byte for byte. The one allowance is a single trailing
# newline on either side, which is how the seats' own read-backs compared.
body_reads_back() { # live body text, wanted body text -> 0 when they agree
  [ "${1-}" = "${2-}" ] && return 0
  [ "${1%$'\n'}" = "${2%$'\n'}" ]
}

set_pr_body() { # pr number, body file -> 0 set and read back, 1 write failed, 2 read failed, 3 differs
  local live want rc
  gh api -X PATCH "repos/{owner}/{repo}/pulls/$1" -F "body=@$2" >/dev/null || return 1
  # `x` guards the trailing newlines a command substitution would strip, and
  # the one newline `--jq` appends is removed after it.
  live=$(gh api "repos/{owner}/{repo}/pulls/$1" --jq .body; rc=$?; printf x; exit "$rc")
  rc=$?
  [ "$rc" -eq 0 ] || return 2
  live=${live%x}; live=${live%$'\n'}
  want=$(cat -- "$2"; printf x); want=${want%x}
  body_reads_back "$live" "$want" || return 3
  return 0
}

# The body-then-push arm, a function so the self-test can drive its ORDER with a
# stubbed client and a stubbed push: the body is set and read back first, and a
# body that did not land pushes nothing.
body_then_push() { # pr number, body file
  local why
  set_pr_body "$1" "$2"
  case $? in
    0) ;;
    1) why="the PATCH was refused" ;;
    2) why="the body could not be read back" ;;
    *) why="the body read back differs from $2" ;;
  esac
  if [ -n "${why:-}" ]; then
    say REFUSE "body" "could not set #$1's body; NOTHING was pushed ($why)"; exit 5
  fi
  say ok "body" "#$1 now carries this body, read back; its \`edited\` run fires against the outgoing head"
  push_branch
  say ok "order" "the \`synchronize\` run at $(git rev-parse --short HEAD) reads the body checked above"
}

# --- self-test ---------------------------------------------------------------
# A countermeasure that cannot be shown failing does not merge
# (`.claude/rules/defect-root-cause.md`, "A detector must be shown to detect").
# This drives the decisions above against the same `policy-rot/prepr` fixtures
# `prepr.sh --self-test` uses, and pairs every refusal with the healthy input
# that must NOT be refused -- a check that fires on everything and a check that
# fires on the right thing print the same "refused" line.
#
# It does NOT drive the network: the push and the pull-request calls are
# demonstrated end to end on the pull request that lands a change to them. What
# it does drive with a stubbed `gh` and a stubbed push is the body arm's ORDER
# and WHICH CALL it makes -- the stub refuses `gh pr edit` the way the seat
# token's missing `read:org` does, so the assertion is about this script's
# choice of call and not about the stub's answer.
if [ "${1:-}" = "--self-test" ]; then
  SELF="$(cd "$(dirname -- "$0")" && pwd)/$(basename -- "$0")"
  cd "$(git rev-parse --show-toplevel)" || exit 2
  D=.claude/workflows/fixtures/policy-rot/prepr
  ZERO=0000000000000000000000000000000000000000
  STALE=deadbeefdeadbeefdeadbeefdeadbeefdeadbeef
  # The two listings `gh pr list --json number` actually prints, as literals, so
  # the fixtures are the observed bytes rather than this file's idea of them.
  ONE='[{"number":715}]'
  TWO='[{"number":715},{"number":716}]'
  st_pass=0; st_fail=0
  st() { if [ "$1" = "$2" ]; then st_pass=$((st_pass+1)); printf '  ok   %s\n' "$3";
         else st_fail=$((st_fail+1)); printf '  FAIL %s (got %s, wanted %s)\n' "$3" "$1" "$2"; fi; }

  st "$(head_section_sha "$D/good.md")" "$ZERO" "the head section's SHA is read out of a healthy body"
  st "$(head_section_sha "$D/wrong-head.md")" "$STALE" "and out of the stale-head fixture, which is the defect's shape"
  st "$(head_section_sha "$D/no-figures.md")" "$ZERO" "a body missing a LATER section still has its head read"
  st "$(head_section_sha /dev/null)" "" "a body with no head section yields no SHA"

  # The query's three outcomes, classified from the listing TEXT. The pairing
  # rule this block is built on: every refusal sits beside the healthy input it
  # must NOT refuse, because a classifier that answers `unknown` to everything
  # would satisfy the refusals alone.
  st "$(pr_from_listing 0 '[]')" "none" \
     "an empty listing is a POSITIVE statement that no pull request is open"
  st "$(pr_from_listing 0 "$ONE")" "715" \
     "a listing naming one pull request yields its number"
  st "$(pr_from_listing 0 "$TWO")" "715" \
     "two open pull requests on one head: the first is taken, as the old --jq did"
  st "$(pr_from_listing 1 '')" "unknown" \
     "A QUERY THAT FAILED IS unknown, NOT none -- the shape the fix review blocked on"
  st "$(pr_from_listing 1 '[]')" "unknown" \
     "and a failing status outranks even a well-formed listing (rc is read first)"
  st "$(pr_from_listing 0 '')" "unknown" \
     "exit 0 and nothing printed did not answer either -- gh's --jq does exactly this"
  st "$(pr_from_listing 0 'GraphQL: Could not resolve to a Repository')" "unknown" \
     "prose on stdout is not a listing (null control on the two array cases)"
  # An array-shaped listing carrying no `"number"` field at all. This is the one
  # direction that fails OPEN: the fallthrough must answer `unknown`, and a later
  # edit returning any digit string here would select the body-then-push arm for
  # a pull request that was never identified. Nothing pinned it until a reviewer
  # replaced that fallthrough with a bare number and the suite still passed.
  st "$(pr_from_listing 0 '[{"headRefOid":"deadbeef"}]')" "unknown" \
     "an array with no number field is unknown, not a number"
  st "$(pr_arm "$(pr_from_listing 0 '[{"headRefOid":"deadbeef"}]')")" "refuse" \
     "and that answer refuses rather than pushing"

  st "$(pr_arm none)" "push-then-create" "no pull request: the opened run is the first pr-contract run there is"
  st "$(pr_arm 704)" "body-then-push" "a pull request exists: the body is set before the push, per S10"
  st "$(pr_arm unknown)" "refuse" "an unanswered query picks no arm; the arm that guesses is the one that pushes"
  st "$(pr_arm '')" "refuse" "AN EMPTY ANSWER REFUSES -- it used to read as no pull request, which is the defect"
  st "$(pr_arm '-')" "refuse" "and so does any other non-number: only the literal none selects the push arm"

  # End to end over both functions, because each is right alone only if the
  # composition is. The second line is the null control on the first: the same
  # path still reaches the push arm when the query positively answers `none`.
  st "$(pr_arm "$(pr_from_listing 1 '')")" "refuse" \
     "a query that failed while a pull request exists does NOT select push-then-create"
  st "$(pr_arm "$(pr_from_listing 0 '[]')")" "push-then-create" \
     "and a query that answered none still does (null control on the refusal above)"
  st "$(pr_arm "$(pr_from_listing 0 "$ONE")")" "body-then-push" \
     "and a query that named one still sets the body first"

  approval_prefix_agrees "policy: x" "policy: x"; st $? 0 "a policy title over a policy subject agrees"
  approval_prefix_agrees "fix: x" "fix: x";       st $? 0 "a non-policy pair agrees (null control)"
  approval_prefix_agrees "policy: x" "fix: x";    st $? 1 "a policy title over a non-policy subject disagrees (the WARN arm)"
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
  # The code-fence guard, which nothing pinned until a reviewer mutated it away
  # and the suite still printed a clean pass. A `## Head` section containing a
  # fenced block is refused rather than rewritten, because `awk` would drop the
  # fence's contents along with the section and the loss is silent.
  printf '## Head\n\n```\ngit rev-parse HEAD\n```\n\n## Figures\n' > "$W/fenced.md"
  write_head "$W/fenced.md" "$ZERO"; st $? 2 "write_head refuses a \`## Head\` section containing a code fence"
  st "$(grep -c '^```' "$W/fenced.md")" "2" "and leaves the fenced body untouched (null control on the refusal)"
  printf 'no head section here\n' > "$W/nohead.md"
  write_head "$W/nohead.md" "$ZERO"; st $? 1 "write_head refuses a body with no \`## Head\` heading"
  st "$(cat "$W/nohead.md")" "no head section here" "and leaves that body untouched"

  # THE SECTION IS A RECORD, NOT A SLOT. `## Head` in this programme carries the
  # round-by-round history beside the SHA, and a repair that replaces the WHOLE
  # section deletes that history every time a seat pushes, which is the tool
  # destroying the record it exists to protect.
  # The contract it serves never asked for that: `checkPrBody`'s head test is
  # `headSec.includes(head) || headSec.includes(head.slice(0, 7))`, a SUBSTRING
  # over the section, so naming the SHA is enough and the rest may stay.
  #
  # The stale direction is the hard one, and it is driven against `policy_lint`
  # itself rather than against this file's reader, both ways round: the new head
  # must be named and the old one must NOT, or a section that named both would
  # satisfy the check at either and the "does not name" refusal would stop
  # refusing anything.
  OLD=1111111111111111111111111111111111111111
  KEEP=abc1234
  mk_body() { # file, the `## Head` section's content
    printf '## Head\n\n%s\n\n## Mutation proof\n\nm\n\n## Null control\n\nn\n\n## Figures\n\nf\n\n## Red checks\n\nnone\n\n## Forward-carry\n\nnone\n\n## Friction\n\nnone\n' "$2" > "$1"
  }
  mk_body "$W/prose.md" "\`$OLD\`

Round one was measured at \`$KEEP\` and the prose says why."
  cp "$W/prose.md" "$W/prose.before"
  WARN=$(write_head "$W/prose.md" "$ZERO" 2>&1 >/dev/null)
  st $? 0 "write_head succeeds on a \`## Head\` section carrying prose beside the SHA"
  st "$(head_section_sha "$W/prose.md")" "$ZERO" "and the section names the head it was given"
  st "$(grep -c 'the prose says why' "$W/prose.md")" "1" \
     "AND THE PROSE SURVIVED -- the section is the record, not a slot for one token"
  st "$(wc -l < "$W/prose.md" | tr -d ' ')" "$(wc -l < "$W/prose.before" | tr -d ' ')" \
     "the repair substitutes one line rather than truncating the section (line count unchanged)"
  st "$(grep -c "$KEEP" "$W/prose.md")" "1" \
     "an unrelated SHA the record cites is left where it stands"
  node .claude/workflows/policy_lint.mjs --pr-body "$W/prose.md" --head "$ZERO" >/dev/null 2>&1
  st $? 0 "the repaired body passes the contract check at the new head"
  node .claude/workflows/policy_lint.mjs --pr-body "$W/prose.md" --head "$OLD" >/dev/null 2>&1
  st $? 1 "AND IS REFUSED AT THE SUPERSEDED ONE -- naming both would empty the \`does not name\` refusal"
  st "$WARN" "" \
     "nothing warned: the superseded SHA is gone from the section (null control on the warn below)"
  # The null control on the repair itself: a body that already names the head is
  # not rewritten at all. A repair that reformats on every run would still pass
  # every assertion above and would churn the record once per push.
  cp "$W/prose.md" "$W/again.md"
  write_head "$W/again.md" "$ZERO"; st $? 0 "write_head succeeds on a body that already names the head"
  if cmp -s "$W/again.md" "$W/prose.md"; then IDENT=same; else IDENT=differs; fi
  st "$IDENT" "same" "and leaves it BYTE-IDENTICAL rather than rewriting it"
  # THE SAME NULL CONTROL WITH THE DECLARATION ABBREVIATED, which is the one that
  # is not vacuous. Rewriting a 40-character SHA over itself is byte-identical
  # whether or not the no-write path exists, so the assertion above passes even
  # with that path deleted; over `0000000` it does not, and only `sha_names`
  # reading the abbreviation as the same commit keeps the body untouched.
  mk_body "$W/abbrev.md" "\`$(printf '%s' "$ZERO" | cut -c1-7)\`

Round one, and this sentence is the record."
  cp "$W/abbrev.md" "$W/abbrev.before"
  write_head "$W/abbrev.md" "$ZERO"; st $? 0 "write_head succeeds on a section declaring an ABBREVIATED head"
  if cmp -s "$W/abbrev.md" "$W/abbrev.before"; then IDENT=same; else IDENT=differs; fi
  st "$IDENT" "same" "and leaves THAT byte-identical too: an abbreviation names the same commit"
  node .claude/workflows/policy_lint.mjs --pr-body "$W/abbrev.md" --head "$ZERO" >/dev/null 2>&1
  st $? 0 "which the contract check accepts, because its test is a substring of the 7-prefix"
  # No SHA in the section at all: there is nothing to substitute, so the SHA is
  # inserted under the heading and the prose still stays.
  mk_body "$W/nosha.md" "This section has prose and names no commit at all."
  write_head "$W/nosha.md" "$ZERO"; st $? 0 "write_head succeeds on a section that names no SHA"
  st "$(head_section_sha "$W/nosha.md")" "$ZERO" "and inserts the head under the heading"
  st "$(grep -c 'names no commit at all' "$W/nosha.md")" "1" "leaving that section's prose in place"
  node .claude/workflows/policy_lint.mjs --pr-body "$W/nosha.md" --head "$ZERO" >/dev/null 2>&1
  st $? 0 "and the inserted body passes the contract check"
  # THE RESIDUAL, STATED AND PINNED. Preserving the section means a superseded
  # SHA the PROSE also cites survives, and `includes` would then be satisfied at
  # that old head. It is warned rather than refused, on this file's own
  # `approval_prefix_agrees` precedent: rewriting the record to satisfy a
  # substring check is the defect, and a check that blocks the legitimate path
  # is one a seat routes around.
  mk_body "$W/echoed.md" "\`$OLD\`

The third round was measured at \`$OLD\`, which is what this sentence is about."
  WARN=$(write_head "$W/echoed.md" "$ZERO" 2>&1 >/dev/null)
  st $? 0 "a section whose PROSE also cites the superseded SHA is still repaired"
  st "$(head_section_sha "$W/echoed.md")" "$ZERO" "and still names the new head first"
  case "$WARN" in *1111111*) WSEEN=named ;; *) WSEEN="$WARN" ;; esac
  st "$WSEEN" "named" "and it WARNS, naming the superseded SHA still standing in the prose"
  st "$(grep -c 'what this sentence is about' "$W/echoed.md")" "1" \
     "rather than editing the record to suit the check"

  # THE BODY ARM, over a stubbed client and a stubbed push. The stub answers the
  # REST PATCH and GET the arm is meant to make, and refuses `gh pr edit` with
  # the scope error the seat token gets, so restoring that call turns these red.
  # Every refusal is paired with the healthy run beside it, and each run's log
  # says whether PUSH was reached and in which position.
  mkdir -p "$W/bin"
  cat > "$W/bin/gh" <<'STUB'
#!/bin/bash
S="${PUSH_STUB_DIR:?}"; printf '%s\n' "$*" >> "$S/log"
if [ "${1:-}" = "pr" ] && [ "${2:-}" = "edit" ]; then
  echo "GraphQL: Your token has not been granted the required scopes to execute this query. The 'login' field requires one of the following scopes: ['read:org']" >&2
  exit 1
fi
[ "${1:-}" = "api" ] || exit 9
patch=0; path=""; file=""; jq=""
shift
while [ $# -gt 0 ]; do
  case "$1" in
    -X) [ "$2" = "PATCH" ] && patch=1; shift 2 ;;
    -F) case "$2" in body=@*) file="${2#body=@}" ;; esac; shift 2 ;;
    --jq) jq="$2"; shift 2 ;;
    repos/*) path="$1"; shift ;;
    *) exit 9 ;;
  esac
done
case "$path" in 'repos/{owner}/{repo}/pulls/'[0-9]*) ;; *) exit 9 ;; esac
if [ "$patch" = 1 ]; then
  [ -f "$S/refuse-patch" ] && exit 1
  [ -n "$file" ] && cp "$file" "$S/live" && printf '{}\n'; exit $?
fi
[ "$jq" = ".body" ] || exit 9
[ -f "$S/refuse-get" ] && exit 1
cat "$S/live"; [ -f "$S/mangle" ] && printf 'appended by someone else\n'
printf '\n'
STUB
  chmod +x "$W/bin/gh"
  printf '## Head\n\n`%s`\n\nbody text\n' "$ZERO" > "$W/arm.md"
  arm_run() { # stub dir -> the arm's rc; PUSH is appended to the log when reached
    ( export PUSH_STUB_DIR="$1" PATH="$W/bin:$PATH"
      say() { printf '%s\n' "$*" >> "$PUSH_STUB_DIR/said"; }
      push_branch() { printf 'PUSH\n' >> "$PUSH_STUB_DIR/log"; }
      body_then_push 4242 "$W/arm.md" ) >/dev/null 2>&1
  }
  S1="$W/s1"; mkdir -p "$S1"; : > "$S1/log"
  arm_run "$S1"; st $? 0 "the body arm sets the body with the seat token's scopes and succeeds"
  st "$(grep -c '^api -X PATCH repos/{owner}/{repo}/pulls/4242 -F body=@' "$S1/log")" "1" \
     "and it wrote the body with one REST PATCH, not gh pr edit"
  st "$(grep -c '^pr edit' "$S1/log")" "0" "gh pr edit was not called at all"
  st "$(cut -d' ' -f1-3 "$S1/log" | tr '\n' '|')" "api -X PATCH|api repos/{owner}/{repo}/pulls/4242 --jq|PUSH|" \
     "in order: the write, then the read-back, then the push, and nothing else"
  if cmp -s "$S1/live" "$W/arm.md"; then IDENT=same; else IDENT=differs; fi
  st "$IDENT" "same" "and the live body is byte-identical to the checked body file"
  # Null control: a pull request whose body is ALREADY this body still passes,
  # so a push that changes nothing about the body is not refused.
  : > "$S1/log"
  arm_run "$S1"; st $? 0 "an unchanged body passes the arm again (null control)"
  st "$(tail -1 "$S1/log")" "PUSH" "and still reaches the push"
  S2="$W/s2"; mkdir -p "$S2"; : > "$S2/log"; : > "$S2/refuse-patch"
  arm_run "$S2"; st $? 5 "a refused PATCH refuses the arm"
  st "$(grep -c '^PUSH' "$S2/log")" "0" "and NOTHING was pushed"
  st "$(grep -c "could not set #4242's body; NOTHING was pushed (the PATCH was refused)" "$S2/said")" "1" \
     "and the refusal keeps its message and names the stage that failed"
  S3="$W/s3"; mkdir -p "$S3"; : > "$S3/log"; : > "$S3/mangle"
  arm_run "$S3"; st $? 5 "a body that reads back different refuses, though the PATCH returned 0"
  st "$(grep -c '^PUSH' "$S3/log")" "0" "and NOTHING was pushed"
  st "$(grep -c "(the body read back differs from" "$S3/said")" "1" "and names the difference as the reason"
  S4="$W/s4"; mkdir -p "$S4"; : > "$S4/log"; : > "$S4/refuse-get"
  arm_run "$S4"; st $? 5 "a body that cannot be read back refuses"
  st "$(grep -c '^PUSH' "$S4/log")" "0" "and NOTHING was pushed"
  st "$(grep -c "(the body could not be read back)" "$S4/said")" "1" \
     "and names the failed read, not a difference (the read's status is read)"
  # The stub proves the FUNCTION's call; these two prove the script still routes
  # the arm through it. Restoring the old inline `gh pr edit` beside the stubbed
  # function would leave every assertion above green.
  st "$(grep -nE '(^|[;&|(]|[$][(])[[:space:]]*gh[[:space:]]+pr[[:space:]]+edit' "$SELF" | grep -cvE '^[0-9]+:[[:space:]]*#')" "0" \
     "no line of this script invokes gh pr edit"
  st "$(grep -cE '^[[:space:]]*body_then_push "[$]PR" "[$]BODY"$' "$SELF")" "1" \
     "and the body-then-push arm calls body_then_push"
  body_reads_back "a
" "a";                              st $? 0 "one trailing newline is allowed on the live side"
  body_reads_back "a" "a
";                                  st $? 0 "and on the wanted side"
  body_reads_back "a" "a ";         st $? 1 "a trailing space is a difference (null control on the allowance)"
  body_reads_back "a

" "a";                              st $? 1 "and so are two trailing newlines"
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
  say WARN "title" "the title and the last commit's subject disagree about the \`policy:\` prefix, which is one of the two keys that require \`## Approval\` -- locally read off the subject, in CI off the title. The other key, the diff, is derived identically on both sides and the check below does cover it. THE LOCAL PASS BELOW IS NOT EVIDENCE ABOUT THE TITLE ARM: either carry the section anyway, or make the subject the title the pull request will have."
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
    0) if sha_names "$WAS" "$HEAD_SHA"; then say ok "head" "already $(git rev-parse --short HEAD), and nothing was rewritten"
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

PR_LISTING=$(gh pr list --head "$BR" --state open --json number 2>/dev/null); PR_RC=$?
PR=$(pr_from_listing "$PR_RC" "$PR_LISTING")
ARM=$(pr_arm "$PR")
if [ "$ARM" = "refuse" ]; then
  say REFUSE "pr query" "the pull-request query neither named an open pull request on $BR nor stated that none is open (it exited $PR_RC and returned <<$PR_LISTING>>), so which arm is correct is not known and NOTHING was pushed. Pushing on a guess is the defect this script exists to prevent: if one is in fact open, the push writes its \`synchronize\` run against whatever stale body it carries. Re-run when the pull-request surface answers, or drive the arm by hand -- see .claude/workflows/web-fragments.md."
  exit 4
fi
if [ "$PR" = "none" ]; then say arm "$ARM" "no pull request is open on $BR"
else say arm "$ARM" "#$PR on branch $BR"; fi

push_branch() {
  git push --set-upstream origin "$BR" || { say REFUSE "push" "git push failed"; exit 5; }
  say ok "push" "origin/$BR at $(git rev-parse --short HEAD)"
}

if [ "$NO_PR" = "1" ]; then
  # The escape exists so an interim push does not need a pull request to exist
  # first. It is refused once one does, because at that point skipping the body
  # write IS the defect: the `synchronize` run would read whatever body the
  # pull request happens to carry.
  if [ "$PR" != "none" ]; then
    say REFUSE "--no-pr" "#$PR is open on $BR, so a push writes its \`synchronize\` run against the body already there. Run without --no-pr."
    exit 3
  fi
  push_branch
  say note "--no-pr" "no pull request was opened; run this again without --no-pr to open one with this body"
  exit 0
fi

if [ "$ARM" = "body-then-push" ]; then
  body_then_push "$PR" "$BODY"
else
  push_branch
  URL=$(gh pr create --base main --head "$BR" --title "$TITLE" --body-file "$BODY") || {
    # This message asserts nothing about whether a pull request exists. It used
    # to say "open one", which was wrong on the path a fix review actually hit:
    # the query had failed while a pull request WAS open, the push arm ran, and
    # the create step then refused -- telling the seat to open a pull request
    # that was already open, and saying nothing about the stale body now sitting
    # at the pushed head. The query arm above closes that path; the message is
    # repaired anyway, because `gh pr create` has other ways to fail.
    say REFUSE "create" "the branch reached the remote and \`gh pr create\` failed, so no pull request was opened FROM HERE. If one is already open on $BR its body is now STALE at the pushed head -- set it from $BODY. If none is open, open one with $BODY. Either way, do not let a stub body reach it"; exit 5; }
  say ok "create" "$URL"
  say ok "order" "the \`opened\` run is the first \`pr-contract\` run on this branch and reads the body checked above"
fi

echo
echo "PUSHED: $HEAD_SHA $BR"
