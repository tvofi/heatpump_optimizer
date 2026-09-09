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

[ $rc -eq 0 ] && say clean "no refusal (the 'check' lines above are yours to answer)"
exit $rc
