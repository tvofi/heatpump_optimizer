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
# The handoff gate (dev/audit/rca/R10-HANDOFF-PREPR-BOUNCE.md, M2): the static
# predictor, over the code head this body describes (the checkout it runs in),
# refuses before the push a head that `open_pr.sh`'s prepr step 6d would refuse
# for a reason a static read names. Seconds, where a full prepr here (M1) costs
# minutes on every handoff and failed the RCA's cost test. Its output names
# each arm's repair (M3). A checkout with no predictor is refused, never passed.
ROOT=$(git rev-parse --show-toplevel)
[ -f "$ROOT/tools/pr/ci_predict.py" ] || { echo "body_push: $ROOT carries no tools/pr/ci_predict.py; run it from the code head's worktree" >&2; exit 1; }
if ! PRED=$(cd "$ROOT" && PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main 2>&1); then
  printf '%s\n' "$PRED" >&2
  echo "body_push: the predictor refuses this head (above); repair it, push the code, then the body" >&2
  exit 1
fi
P=""
# The parent is what ORIGIN ANSWERED, never FETCH_HEAD. `git fetch` rewrites
# FETCH_HEAD as per-worktree state of the checkout it runs in, so any other
# fetch landing between the fetch below and the read -- a sibling seat, the
# orchestrator, a watcher -- substitutes an unrelated ref's tip and the push is
# refused non-fast-forward (R9-RC-BUS-FETCHHEAD: the predicate bus.sh carried).
# The fetch stays for the objects: commit-tree cannot write a parent it cannot
# read.
tip=$(git ls-remote origin "refs/heads/$REF" 2>/dev/null | awk 'NF { print $1; exit }') || tip=""
if [ -n "$tip" ]; then
  git fetch -q origin "refs/heads/$REF" || { echo "body_push: could not fetch $REF" >&2; exit 1; }
  P="-p $tip"
fi
{ printf '100644 blob %s\tBODY.md\n' "$(git hash-object -w -- "$BODY")"
  [ -z "$NOTE" ] || printf '100644 blob %s\tRESUME.md\n' "$(git hash-object -w -- "$NOTE")"
} > "${TMPDIR:-/tmp}/body_push.$$"
TREE=$(git mktree < "${TMPDIR:-/tmp}/body_push.$$")
rm -f "${TMPDIR:-/tmp}/body_push.$$"
# shellcheck disable=SC2086 # $P is empty or exactly "-p <sha>"
C=$(git commit-tree "$TREE" $P -m "body: $TOPIC")
# The topic names the ref and the message: refuse one that names this host (#2310).
python3 -I "$(dirname "$0")/ref_privacy.py" guard --ref "$REF" --message "body: $TOPIC"
git push -q origin "$C:refs/heads/$REF"
echo "$REF $C"
