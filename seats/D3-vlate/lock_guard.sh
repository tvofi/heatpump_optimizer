#!/bin/bash
# VD3L environment workaround (not pushed to any tracked file): twice (2 of 13 gate runs) an empty
# index.lock appeared in the baseline worktree ~15 min into a gate with no git process holding it,
# and fullgate.py's post-gate reset then failed. Remove such a lock once it is >120 s old and no git
# process runs; log every removal.
L=/home/user/heatpump_optimizer/.git/worktrees/audit-r11-d3l-base/index.lock
while true; do
  if [ -f "$L" ] && [ ! -s "$L" ] && [ $(( $(date +%s) - $(stat -c %Y "$L") )) -gt 120 ] && ! pgrep -x git >/dev/null; then
    rm -f "$L" && echo "$(date -u +%FT%TZ) removed stale empty index.lock" >> /root/vout/D3-vlate/gates/lock_guard.log
  fi
  grep -q 'CHAIN DONE' /root/vout/D3-vlate/gates/chain.log 2>/dev/null && [ -f /root/vout/D3-vlate/gates/c38d53ab787ddbfa.done ] && break
  sleep 20
done
