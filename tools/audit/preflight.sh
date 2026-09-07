#!/bin/bash
# Pre-flight for ANYTHING the orchestrator publishes: a merge body, an issue
# body, an issue comment, a dispatch brief, a roster edit.
#
# WHY A SCRIPT AND NOT A RESOLUTION. On 2026-09-07 the orchestrator made twelve
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
#    FOUR reference forms, not one. A review found the first version caught only
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

# 3. Bare figures. A count is a measurement; a sliding-window count decays.
n=$(printf '%s' "$body" | grep -oE '\b[0-9]{1,3}(,[0-9]{3})+\b|\b[0-9]+ (of|out of) [0-9]+\b|\b[0-9]+(\.[0-9]+)? ?%|\b[0-9]{2,} [a-z]' | head -8)
[ -n "$n" ] && { say check "figures -- each needs the command that produced it"; printf '%s\n' "$n" | sed 's/^/             /'; }

# 4. The echo-beside-command shape: prints its conclusion whether or not it holds.
if printf '%s' "$body" | grep -qE ';[[:space:]]*echo .*(identical|clean|empty|untouched|passed|none)'; then
  say REFUSE "a conclusion echoed after ';' -- it prints either way; use '&& echo'"
  rc=1
fi

[ $rc -eq 0 ] && say clean "no refusal (the 'check' lines above are yours to answer)"
exit $rc
