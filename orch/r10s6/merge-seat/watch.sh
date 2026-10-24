#!/bin/bash
# exits when queue changes or main push CI changes; touches alive each step
Q=/Users/timmalmstrom/hpo-orch/r10s6/merge-queue.txt
A=/Users/timmalmstrom/hpo-orch/r10s6/merge.alive
qh0=$(md5 -q $Q); ci0=$(cd /Users/timmalmstrom/hpo-seats/r10s6/orch-wt && gh run list --branch main --event push --workflow CI --limit 1 2>/dev/null | head -1 | cut -f1,2,7)
end=$(( $(date +%s) + 6600 )); n=0
while [ $(date +%s) -lt $end ]; do
  for i in 1 2 3 4 5 6 7 8 9 10 11 12; do sleep 25; touch $A; [ "$(md5 -q $Q)" != "$qh0" ] && { echo QUEUE-CHANGED; exit 0; }; done
  ci=$(cd /Users/timmalmstrom/hpo-seats/r10s6/orch-wt && gh run list --branch main --event push --workflow CI --limit 1 2>/dev/null | head -1 | cut -f1,2,7)
  [ -n "$ci" ] && [ "$ci" != "$ci0" ] && { echo "CI-CHANGED $ci"; exit 0; }
done
echo WINDOW-END
