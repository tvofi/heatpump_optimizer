#!/bin/bash
# wait_ref.sh <ref> [<old-sha>] [<every-seconds>]: exit 0 (printing the new
# sha) when <ref> on origin differs from <old-sha>; the cloud seat's last step
# pushes that ref, so this process ending is the orchestrator's wake signal.
# Polls with ls-remote (git protocol, not the REST quota); default every 120 s.
ref=$1; old=${2:-$(git -C /Users/timmalmstrom/hpo-seats/r10s3/orch-wt ls-remote origin "$ref" | cut -f1)}; every=${3:-120}
echo "wait_ref: $ref from ${old:-<absent>} every ${every}s"
while :; do
  now=$(git -C /Users/timmalmstrom/hpo-seats/r10s3/orch-wt ls-remote origin "$ref" | cut -f1)
  rc=$?
  [ $rc -ne 0 ] && { echo "wait_ref: ls-remote rc=$rc, retrying"; sleep "$every"; continue; }
  [ -n "$now" ] && [ "$now" != "$old" ] && { echo "MOVED $ref $old -> $now"; exit 0; }
  sleep "$every"
done
