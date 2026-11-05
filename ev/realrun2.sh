#!/bin/bash
# Real prepr.sh at the handoff code head; mid-run the seat commits new code and points the body's ## Head at it.
B=/tmp/claude-0/rv/body/body.md; cp /tmp/claude-0/rv/body/body.orig $B
cd /tmp/claude-0/rv/wt3; H0=$(git rev-parse HEAD); echo "start HEAD=$H0 $(date -u +%T)"
( sleep 240; printf '# reviewer: code committed while prepr ran\n' >> tools/audit/seat/open_pr.sh
  git -c user.name=r -c user.email=r@x commit -qam 'mid-run commit'; N=$(git rev-parse HEAD); sed -i "s/$H0/$N/g" $B
  echo "mid-run commit $N, body Head now names it $(date -u +%T)" ) &
PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh $B > /tmp/claude-0/rv/ev/realrun2-prepr.log 2>&1; rc=$?; wait
echo "prepr rc=$rc end $(date -u +%T)"; grep -E 'receipt|^PRE-PR' /tmp/claude-0/rv/ev/realrun2-prepr.log
f=$(git rev-parse --absolute-git-dir)/hpo-prepr-receipt; [ -f "$f" ] && echo "receipt file: $(cat $f)" || echo "receipt file: none"
echo "measured start HEAD=$H0 ; HEAD now=$(git rev-parse HEAD)"
grep -E '^\s*(REFUSE|FAIL)' /tmp/claude-0/rv/ev/realrun2-prepr.log | cut -c1-250
