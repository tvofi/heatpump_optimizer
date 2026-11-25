#!/bin/bash
# VD3L: rebuild the report and checkpoint whenever a new gate finishes; exit when the chain is done.
. $HOME/.boxcomms.env
D=$HOME/vout/D3-vlate; seen=$(ls $D/gates/*.done 2>/dev/null | wc -l)
while true; do
  n=$(ls $D/gates/*.done 2>/dev/null | wc -l)
  if [ "$n" != "$seen" ]; then seen=$n; python3 $D/build_report.py >> $D/ckpt_watch.log 2>&1; (cd $REPO && bash $HOME/box_comms.sh checkpoint D3-vlate $D) >> $D/ckpt_watch.log 2>&1; echo "$(date -u +%FT%TZ) ckpt n=$n rc=$?" >> $D/ckpt_watch.log; fi
  grep -q 'CHAIN DONE' $D/gates/chain.log && break
  sleep 60
done
