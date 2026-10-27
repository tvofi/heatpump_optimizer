#!/usr/bin/env bash
# Reviewer-built instrument (fix-review.md step 9: disclosed as mine, not the finder's).
# The narrowed test the record proposes: a handoff-body/ ref is EXEMPT from the OWED
# channel iff (marker AND no owed text), where
#   marker    := first non-blank line matches ^#{1,6}[[:space:]]*STOP:
#   owed text := a line matching ^#{1,6}[[:space:]]*What is owed   (case-insensitive)
# "owed" here is MY definition of "owed text"; the record names only the literal
# heading "## What is owed" and states no matcher.
set -u
body_has_marker() { grep -m1 -v '^[[:space:]]*$' "$1" | grep -qE '^#{1,6}[[:space:]]*STOP:'; }
body_has_owed()   { grep -qiE '^#{1,6}[[:space:]]*What is owed' "$1"; }
# Prints EXEMPT or OWED for one BODY file.
classify() {
  local f="$1" m=no o=no
  body_has_marker "$f" && m=yes
  body_has_owed   "$f" && o=yes
  if [ "$m" = yes ] && [ "$o" = no ]; then echo EXEMPT; else echo OWED; fi
}
for f in "$@"; do
  printf 'RESULT %-40s marker=%-3s owed=%-3s -> %s\n' \
    "$(basename "$f")" \
    "$(body_has_marker "$f" && echo yes || echo no)" \
    "$(body_has_owed   "$f" && echo yes || echo no)" \
    "$(classify "$f")"
done
