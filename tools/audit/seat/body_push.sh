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
# The pr-body gate (dev/audit/rca/R10-RCA-BODY-LINT.md). A body for the head
# published at handoff/<topic> is the pull-request body `open_pr.sh` lints in
# prepr step 7, so that step runs here first (`prepr.sh --body-check`, this
# script's sibling copy) and its refusal is this push's. No handoff/<topic>
# means a result (probe, design, verdict), which is no PR body. A handoff/<topic>
# that is not this checkout's HEAD names a head the open will not run on.
HERE=$(cd "$(dirname "$0")" && pwd)
HREF=$(git ls-remote origin "refs/heads/handoff/$TOPIC") || { echo "body_push: could not read handoff/$TOPIC from origin" >&2; exit 1; }
HREF=$(printf '%s\n' "$HREF" | awk 'NF { print $1; exit }')
if [ -n "$HREF" ]; then
  [ "$HREF" = "$(git -C "$ROOT" rev-parse HEAD)" ] || { echo "body_push: handoff/$TOPIC is at ${HREF:0:12}, this checkout at $(git -C "$ROOT" rev-parse --short=12 HEAD); push the code, then the body" >&2; exit 1; }
  ABS=$(cd "$(dirname "$BODY")" && pwd)/$(basename "$BODY")
  if ! LINT=$(cd "$ROOT" && bash "$HERE/../../pr/prepr.sh" --body-check "$ABS" 2>&1); then
    printf '%s\n' "$LINT" >&2
    echo "body_push: the pr-body lint refuses this body (above), as open_pr.sh's prepr step 7 would; repair it and push again" >&2
    exit 1
  fi
  printf '%s\n' "$LINT" | tail -1
else
  echo "body_push: no handoff/$TOPIC on origin, so a result body: the pr-body lint does not apply"
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
