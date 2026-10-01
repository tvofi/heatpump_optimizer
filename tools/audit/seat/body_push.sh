#!/bin/bash
# body_push.sh <topic> <body.md> [note.md]
# Publishes a handoff's transport on the orphan ref handoff-body/<topic>, so it
# never enters the code head's ancestry (`prepr.sh` step 1a refuses that).
# Each call appends one commit whose tree is BODY.md, plus RESUME.md when a note
# is given. The first commit has no parent, so the ref shares no history with
# the code; later ones are fast-forwards, so a re-bodied handoff needs neither a
# force-push nor a `-vN` branch. A fetch that fails for any reason but a missing
# ref leaves a parentless commit the push then refuses as a non-fast-forward,
# never a rewrite. `handoff_push.sh` reads BODY.md from the ref's tip.
# Plain variables, no arrays: macOS /bin/bash 3.2 rejects an empty array under -u.
set -euo pipefail
TOPIC=${1:?topic}; BODY=${2:?body file}; NOTE=${3:-}
REF=handoff-body/$TOPIC
[ -f "$BODY" ] || { echo "body_push: no body at $BODY" >&2; exit 2; }
[ -z "$NOTE" ] || [ -f "$NOTE" ] || { echo "body_push: no note at $NOTE" >&2; exit 2; }
P=""
if git ls-remote --exit-code -q origin "refs/heads/$REF" >/dev/null 2>&1; then
  git fetch -q origin "refs/heads/$REF"
  P="-p $(git rev-parse FETCH_HEAD)"
fi
{ printf '100644 blob %s\tBODY.md\n' "$(git hash-object -w -- "$BODY")"
  [ -z "$NOTE" ] || printf '100644 blob %s\tRESUME.md\n' "$(git hash-object -w -- "$NOTE")"
} > "${TMPDIR:-/tmp}/body_push.$$"
TREE=$(git mktree < "${TMPDIR:-/tmp}/body_push.$$")
rm -f "${TMPDIR:-/tmp}/body_push.$$"
# shellcheck disable=SC2086 # $P is empty or exactly "-p <sha>"
C=$(git commit-tree "$TREE" $P -m "body: $TOPIC")
git push -q origin "$C:refs/heads/$REF"
echo "$REF $C"
