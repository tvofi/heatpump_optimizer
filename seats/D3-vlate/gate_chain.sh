#!/bin/bash
# VD3L: run the null full gate, then each finding's mutant, one at a time, in the baseline tree.
. $HOME/.boxcomms.env
B=/home/user/audit-r11-d3l-base
O=$HOME/vout/D3-vlate/gates; mkdir -p $O
cd $B
run() {  # name, args...
  local n=$1; shift
  [ -f $O/$n.done ] && return
  echo "$(date -u +%FT%TZ) START $n load1=$(cut -d' ' -f1 /proc/loadavg)" >> $O/chain.log
  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py "$@" > $O/$n.out 2>&1
  echo "rc=$?" >> $O/$n.out
  cp dev/audit/rounds/round11/D3/s1/state/gates/$( [ $n = null ] && echo null || echo $n ).json $O/$n.json 2>/dev/null
  cp dev/audit/rounds/round11/D3/s1/state/gates/$( [ $n = null ] && echo null || echo $n ).log $O/$n.log 2>/dev/null
  touch $O/$n.done
  echo "$(date -u +%FT%TZ) END $n $(grep -E '^VERDICT|gate_rc' $O/$n.out | tr '\n' ' ')" >> $O/chain.log
  (cd $REPO && bash $HOME/box_comms.sh heartbeat "gate $n done") >/dev/null 2>&1
}
run null null
for pair in c2:d931ab195b940b0c pre:121362d48b408236 c2:95779f9d6d71c50d c3c6:5cc84148fa68bda1 pre:0c3e91a6a349409a c2:a0b3b28854fa500c pre:050fdc4a20eba212 c3c6:22b5ec8775d5bd50 c3c6:0911281eca895664 c3c6:5e8d48eff7e4fa8d c2:c38d53ab787ddbfa; do
  while [ -f $O/STOP ]; do sleep 60; done
  run ${pair#*:} run --src ${pair%%:*} --key ${pair#*:}
done
echo "$(date -u +%FT%TZ) CHAIN DONE" >> $O/chain.log
