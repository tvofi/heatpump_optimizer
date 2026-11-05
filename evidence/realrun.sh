#!/bin/bash
# Real prepr.sh at the head with a commit of new code landing mid-run; then read the receipt.
cd /tmp/claude-0/rv/wt3; H0=$(git rev-parse HEAD); echo "start HEAD=$H0 $(date -u +%T)"
( sleep 180; printf '# reviewer: code committed while prepr ran\n' >> tools/audit/seat/open_pr.sh
  git -c user.name=r -c user.email=r@x commit -qam 'mid-run commit' && echo "mid-run commit $(git rev-parse HEAD) $(date -u +%T)" ) &
PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh /tmp/claude-0/rv/body/body.md > /tmp/claude-0/rv/ev/realrun-prepr.log 2>&1; rc=$?; wait
echo "prepr rc=$rc end $(date -u +%T)"; grep -E 'receipt|^PRE-PR' /tmp/claude-0/rv/ev/realrun-prepr.log
f=$(git rev-parse --absolute-git-dir)/hpo-prepr-receipt; [ -f "$f" ] && echo "receipt file: $(cat $f)" || echo "receipt file: none"
echo "measured start HEAD=$H0 ; HEAD now=$(git rev-parse HEAD)"
