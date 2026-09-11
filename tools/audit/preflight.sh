#!/bin/bash
# Pre-flight for ANYTHING the orchestrator publishes: a merge body, an issue
# body, an issue comment, a dispatch brief, a roster edit.
#
# WHY A SCRIPT AND NOT A RESOLUTION. On 2026-09-07 the orchestrator made a run of
# unmeasured claims, every one caught by a review seat and none by itself, while
# actively writing the policy against them. Intentions did not bind. The one
# mechanical check built that day (closing keywords) caught a real defect on the
# very next merge. So: mechanical, run every time, refuses rather than warns.
#
# Usage: preflight.sh [intended-issue-numbers...] < text
set -uo pipefail
intended=" $* "
body=$(cat)
rc=0
say() { printf '  %-8s %s\n' "$1" "$2"; }

# 1. Closing keywords. GitHub's own rule: KEYWORD [:] WS #N, no intervening
#    words -- and it discards negation, so "does not close #224" closes #224.
while read -r kw num; do
  [ -z "${num:-}" ] && continue
  case "$intended" in
    *" $num "*) say ok "closes #$num -- intended" ;;
    *) say REFUSE "'$kw #$num' closes #$num; not in the intended list"; rc=1 ;;
  esac
#    FOUR reference forms, not one -- and FOUR IS NOT ALL OF THEM. A review
#    found seven further shapes that still pass, and this grep is line-oriented,
#    so a keyword and a number split across a newline are not seen. Treat the
#    output as a pre-flight that catches the common cases, never as a gate that
#    proves the body is clean. A review found the first version caught only
#    `#N` while GitHub acts on all of these -- so `Closes GH-224` passed clean:
#      #224                                   bare
#      GH-224                                 GH- prefix
#      tvofi/heatpump_optimizer#224           owner/repo
#      https://github.com/tvofi/.../issues/224  full URL
done < <(printf '%s' "$body" \
  | grep -oiE '\b(close[sd]?|fix(e[sd])?|resolve[sd]?)[[:space:]]*:?[[:space:]]+((https?://[^ ]*/issues/|[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#|GH-|#)[0-9]+)' \
  | sed -E 's|^([A-Za-z]+).*[/#-]([0-9]+)$|\1 \2|')

# 2. Unqualified quantifiers. Each needs the whole set enumerated, not sampled.
q=$(printf '%s' "$body" | grep -onE '\b(every|all|each|both|none|never|always|no [a-z]+ (is|are|was|were))\b' | head -8)
[ -n "$q" ] && { say check "quantifiers -- did you enumerate the SET, or sample it?"; printf '%s\n' "$q" | sed 's/^/             /'; }

# 3. Bare figures. A count is a measurement; a sliding-window count decays; and a
#    figure an instrument in the tree prints is stale the moment the tree moves.
#    The body contract's `## Figures` section is where each one names the command
#    that printed it, and writing-for-agents.md says name the instrument rather
#    than restate its output. Advisory, not a refusal: a regex over prose cannot
#    tell a measurement from a threshold, which is what #581 measured and closed on.
n=$(printf '%s' "$body" | grep -oE '\b[0-9]{1,3}(,[0-9]{3})+\b|\b[0-9]+ (of|out of) [0-9]+\b|\b[0-9]+(\.[0-9]+)? ?%|\b[0-9]{2,} [a-z]' | head -8)
[ -n "$n" ] && { say check "figures -- each is in ## Figures with its command, or is an instrument's own output and not restated"; printf '%s\n' "$n" | sed 's/^/             /'; }

# 4. The echo-beside-command shape: prints its conclusion whether or not it holds.
#    An INLINE-backticked occurrence in PROSE is advisory: a body explaining this
#    anti-pattern quotes it, and refusing that is the over-fire that got #581
#    closed. Inside a FENCED block the exemption does not apply. The earlier
#    justification for the split -- "a BARE occurrence is a pasted transcript" --
#    was refuted by a review that smuggled a real transcript through by wrapping
#    the pasted line in backticks inside a fence: two characters turned the
#    refusal into an advisory. Bareness does not identify a pasted transcript;
#    the fence is what carries the evidence claim.
#    LIMITS: ``` fences only, not ~~~. An unterminated fence treats the rest of
#    the body as fenced, which refuses more rather than less.
ECHO_SHAPE=';[[:space:]]*echo .*(identical|clean|empty|untouched|passed|none)'
bare=$(printf '%s' "$body" \
  | awk '/^[[:space:]]*```/ {f = !f; next} !f {gsub(/`[^`]*`/, "")} {print}' \
  | grep -cE "$ECHO_SHAPE")
quoted=$(printf '%s' "$body" | grep -cE "$ECHO_SHAPE")
if [ "$bare" -gt 0 ]; then
  say REFUSE "a conclusion echoed after ';' -- it prints either way; use '&& echo'"
  rc=1
elif [ "$quoted" -gt 0 ]; then
  say check "the '; echo' shape appears in backticks -- an example, not a claim?"
fi

# 5. A STALE POLICY CORPUS. A branch may legitimately carry an old TREE -- one
#    under review is frozen, and a detached review worktree must stay at its head
#    SHA -- but no seat should read an old POLICY corpus. An orchestrator
#    worktree 69 commits behind main dispatched a review seat into a
#    `tools/audit/briefs/fix-review.md` that predated 58aec5f (the verdict
#    grammar) and 43d3e93 (paginated check-runs). Under that text the seat would
#    have written a verdict `web-fix-wave.js` cannot parse and read checks with a
#    call that reports `pr-contract` GREEN at a commit where it was red. It
#    noticed; nothing was corrupted by luck rather than by design.
#
#    STALE, NOT DIFFERENT. "differs from origin/main" fires on exactly the
#    branches doing intentional policy work -- #715 edits fixer.md and
#    orchestrator.md, #722 edits three rule files -- and a predicate that blocks
#    the legitimate path is one a seat routes around. The separation is the whole
#    check: a file origin/main moved since the merge base MINUS the files this
#    branch authored, both three-dot from that base.
#
#    THE RESIDUE IS NAMED, NOT HIDDEN. A file in BOTH sets is based on the old
#    text and is not reported as stale, because reporting it is the false
#    positive above. It gets its own line instead: a rebase has to reconcile it,
#    which is a thing git will say too.
#
#    THE CORPUS IS POLICY_GLOBS, read from policy_lint.mjs rather than copied.
#    CLAUDE.md: a fourth definition of "what is policy" is its own defect. The
#    filter mode is a pure function of the path, so a policy file ADDED on main
#    and absent from this checkout is still classified.
#
#    CHECK, NOT REFUSE, and the reason is structural rather than lenient.
#    (a) Every refusal above is a property of the TEXT ON STDIN -- the author's
#        own artifact, fixable in seconds by editing it. Staleness is a property
#        of the CHECKOUT: no edit to the body clears it, so a refusal here
#        refuses a body that is correct.
#    (b) The repair is `git merge origin/main`, and fixer.md step 6 then
#        re-executes steps 2-8 -- failing test, mutation proof, both harness
#        ends, and the body, whose figures move with origin/main too. Blocking a week-old branch on unrelated work to buy that is the
#        shape prepr.sh's push-order comment refuses: "a refusal here would
#        refuse the prescribed order, which is worse than the defect it answers."
#    (c) NO NETWORK, EVER, as prepr.sh states it: the comparison is against the
#        LOCAL mirror refs/remotes/origin/main. That makes this check too QUIET
#        and never too loud -- an unfetched mirror under-reports, it cannot
#        invent staleness. A refusal resting on evidence that may be stale is
#        dishonest; a warning resting on it is not.
#    (d) tests/entities.py executes this script in CI and asserts exit codes. A
#        refusal arm keyed on repository state would make those pins depend on
#        how recently the runner fetched.
#
#    WHERE IT DOES NOT REACH, stated rather than left to be discovered: this
#    script runs before a PUSH. A fix reviewer never pushes, and the reviewer is
#    the seat this defect actually hurt. So the second home is the review seat's
#    own start-up, and it is carried there rather than left open:
#    tools/audit/briefs/fix-review.md, the paragraph under the detached-worktree
#    preamble, which states the precondition and gives the same comparison as a
#    command a reviewer runs by hand. That edit is a policy change and is
#    surfaced for the owner's approval on the pull request, not folded in
#    silently -- CLAUDE.md wants it opened and surfaced, not withheld.
set_of() { printf '%s\n' "$1" | sed '/^$/d' | sort -u; }
n_of() { set_of "$1" | wc -l | tr -d ' '; }
minus() { comm -23 <(set_of "$1") <(set_of "$2"); }
inter() { comm -12 <(set_of "$1") <(set_of "$2"); }
corpus_filter() { node "$1/.claude/workflows/policy_lint.mjs" --corpus-filter 2>/dev/null; }

why=""; root=""; base=""
if ! root=$(git rev-parse --show-toplevel 2>/dev/null) || [ -z "$root" ]; then
  why="not a git checkout"
elif ! git rev-parse --verify --quiet refs/remotes/origin/main >/dev/null 2>&1; then
  why="no refs/remotes/origin/main in this clone, so there is nothing to compare against"
elif ! base=$(git merge-base refs/remotes/origin/main HEAD 2>/dev/null) || [ -z "$base" ]; then
  why="no common ancestor with origin/main (shallow clone? git fetch --unshallow origin)"
elif ! command -v node >/dev/null 2>&1; then
  why="no node, so POLICY_GLOBS cannot be read and the corpus is undefined here"
#  THE FILTER IS PROBED, NOT ASSUMED. An old checkout's policy_lint.mjs does not
#  know --corpus-filter: it treats the flag as a no-op, lints the whole corpus,
#  and prints FINDINGS on stdout. Read as a path list that is silence, and
#  silence here reads as "current" -- a check that goes green precisely on the
#  stale checkouts it exists to catch. So one sentinel pair decides it: a policy
#  path must come back and a non-policy path must not.
elif [ "$(printf 'CLAUDE.md\ntools/audit/not-a-policy-path.zzz\n' | corpus_filter "$root")" != "CLAUDE.md" ]; then
  why="policy_lint.mjs here does not answer --corpus-filter, so the corpus is undefined (a checkout predating it?)"
fi
if [ -n "$why" ]; then
  say check "policy corpus -- NOT compared: $why"
else
  moved=$(git diff --name-only "$base...refs/remotes/origin/main" 2>/dev/null)
  mine=$(git diff --name-only "$base...HEAD" 2>/dev/null)
  pol=$(printf '%s\n%s\n' "$moved" "$mine" | sed '/^$/d' | sort -u | corpus_filter "$root")
  moved=$(inter "$moved" "$pol")
  mine=$(inter "$mine" "$pol")
  stale=$(minus "$moved" "$mine")
  both=$(inter "$moved" "$mine")
  if [ -n "$stale" ]; then
    say check "policy corpus -- $(n_of "$stale") file(s) origin/main moved since your merge base and this branch does not touch: the copy every seat here reads is not the current contract. Re-read them, or update the branch."
    printf '%s\n' "$stale" | sed 's/^/             /'
  else
    say ok "policy corpus -- current with origin/main ($(n_of "$mine") file(s) authored here, not stale)"
  fi
  [ -n "$both" ] && { say check "policy corpus -- authored here AND moved on origin/main; a rebase reconciles these, so they are not counted stale:"; printf '%s\n' "$both" | sed 's/^/             /'; }
#  THE ONE FALSE NEGATIVE, MADE VISIBLE. Nothing above fetches, so the whole
#  comparison rests on a LOCAL mirror. A worktree that is 59 commits stale and
#  whose mirror was never re-fetched compares e4f34c7 against e4f34c7 and this
#  check reports `ok` -- green on exactly the shape it was written for, which is
#  the failure mode that produced the incident in the first place. It cannot be
#  fixed here (a check that hangs or fails offline is run with `|| true` inside a
#  week), so it is made visible instead, by the one offline proxy there is: main
#  moves several times a day in this repository, so a mirror that has not moved
#  in a day is more likely unfetched than quiet.
#
#  WHAT IS MEASURED IS THE REFLOG ENTRY, NOT THE COMMIT DATE, and the difference
#  is the difference between a local fact and an upstream one. `git log -1
#  --format=%ct` reads when main's tip was COMMITTED, somewhere else, by someone
#  else; a worktree created this minute from a mirror fetched this minute reports
#  30h on a tip committed yesterday, and the line fires on a checkout that is
#  perfectly current. The reflog records when THIS clone last moved the ref.
#
#  It is still an upper bound on "time since fetch" and never a measurement of
#  it: git writes a reflog entry only when the ref MOVES, so a fetch that finds
#  main unchanged leaves the age climbing. That direction is the safe one -- it
#  over-reports age, so the line is too loud and never too quiet, which is the
#  same asymmetry (c) above rests on. A PROXY, not a measurement: it says when to
#  distrust the lines above, and it cannot say they are wrong.
  when=$(git reflog show refs/remotes/origin/main --date=unix --format=%gd 2>/dev/null | head -1 | sed 's/.*@{\([0-9]*\)}.*/\1/')
  what="last moved in this clone"; caveat=""
  case "$when" in
    ''|*[!0-9]*)
      # No reflog for the ref: a --mirror clone, or core.logAllRefUpdates off.
      # Falling back is what stops the proxy vanishing in silence on exactly the
      # clones a review seat runs in -- and the line says which measure it fell
      # back to, because the two answer different questions.
      when=$(git log -1 --format=%ct refs/remotes/origin/main 2>/dev/null)
      what="tip was committed"
      caveat=" (No reflog for the ref in this clone, so that is main's own age and not this mirror's.)"
      ;;
  esac
  case "$when" in
    ''|*[!0-9]*) ;;
    *)
      age=$(( ( $(date +%s) - when ) / 3600 ))
      [ "$age" -ge 24 ] && say check "policy corpus -- refs/remotes/origin/main $what ${age}h ago and nothing here fetches. If that is not main's real tip, everything above compared against a stale mirror and under-reports. \`git fetch origin\`, then re-run.$caveat"
      ;;
  esac
fi

[ $rc -eq 0 ] && say clean "no refusal (the 'check' lines above are yours to answer)"
exit $rc
