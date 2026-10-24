#!/bin/bash
# Polls probe/rev-* refs every 2 min; relays each new one once via relay.sh, then bus.sh confirm; results to owed.log. Log: cloud/relay.log
cd "$(dirname "$0")"; touch relayed
while true; do
  git -C /Users/timmalmstrom/heatpump_optimizer ls-remote origin 'refs/heads/probe/rev-*' | while read s r; do
    k=${r#refs/heads/probe/rev-}; grep -qx "$k $s" relayed && continue
    pr=${k%%-*}; n8=${k#*-}; n=$(awk -v p=$pr -v n=$n8 '$1==p && index($4,n)==1 {print $4}' ~/.zcode/bus/dispatched | tail -1)
    echo "$(date -u +%FT%TZ) relay $pr $n8 $s" >> relay.log
    out=$(./relay.sh "$pr" "$n" 2>&1); rc=$?; echo "$out" >> relay.log
    [ $rc = 0 ] || { echo "$(date -u +%FT%TZ) OWED relay-refused $pr" >> owed.log; continue; }
    echo "$k $s" >> relayed
    rs=$(echo "$out" | awk -v p="review/$pr" '$1==p {print $2}' | tail -1)
    (cd /Users/timmalmstrom/heatpump_optimizer && bash tools/audit/seat/bus.sh confirm "$pr" "$rs") >> relay.log 2>&1 \
      && echo "$(date -u +%FT%TZ) POSTED $pr $(grep "BUS posted $pr" relay.log | tail -1 | cut -c1-160)" >> owed.log \
      || echo "$(date -u +%FT%TZ) OWED confirm $pr $rs" >> owed.log
  done
  sleep 120
done
