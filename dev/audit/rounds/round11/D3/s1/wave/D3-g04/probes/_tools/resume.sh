#!/usr/bin/env bash
# box-local recovery after a container restart: release the dead gate's lease/slot and comms lock,
# drop its partial record, restart the heartbeat loop, the gate driver and the recorder.
. $HOME/.boxcomms.env; L=$HOME/wavelogs; T=$HOME/audit-r11-D3-s1; S1=$T/dev/audit/rounds/round11/D3/s1
pgrep -f 'gate_wave.sh run' >/dev/null && { echo "driver alive, nothing to do"; exit 0; }
rmdir $HOME/.boxcomms-r11-D3-g04/lock 2>/dev/null
k=$(git -C $T log -1 --format=%s | sed -n 's/.*full-gate mutant \([0-9a-f]\{16\}\).*/\1/p')
(cd $T && export PYTHONPATH=tests/hastub && python3 tests/gate_lock.py release --label D3-s1-r11
 for s in $(python3 tests/gate_lock.py slot-status | grep -o 'run.sh-[0-9]*'); do python3 tests/gate_lock.py slot-release --label $s; done)
if [ -n "$k" ] && [ ! -f $S1/wave/$BOX/gates/$k.json ]; then rm -f $S1/state/gates/$k.*; echo "- $(date -u +%FT%TZ) container restart killed gate $k (no record); lease/slots released, re-run." >> $S1/wave/$BOX/NOTES.md; fi
mv $L/run.log $L/run-$(date +%s).log 2>/dev/null
(cd $REPO && bash $HOME/box_comms.sh heartbeat "container restart; recovered${k:+, re-running $k}")
cd $REPO; setsid nohup bash $HOME/box_comms.sh loop 600 >> $L/loop.log 2>&1 < /dev/null &
cd $HOME; setsid nohup bash $HOME/gate_wave.sh run >> $L/run.log 2>&1 < /dev/null &
pgrep -f autorec.sh >/dev/null || setsid nohup bash $HOME/autorec.sh >> $L/rec.log 2>&1 < /dev/null &
sleep 5; cat $L/run.log
