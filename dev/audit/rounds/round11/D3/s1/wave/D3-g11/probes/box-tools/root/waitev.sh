# exit with the first new event line in the gate/recorder/inbox logs after the recorded offsets
S=$HOME/.waitev; touch $S
pat='VERDICT|RECORD|GATES-DONE|REFUSE|Traceback|CMD |STOPPED|checkpoint failed|heartbeat failed|NULL-MISSING'
while true; do
  for f in run.log recorder.log loop.log; do
    p=$HOME/$f; [ -f $p ] || continue
    off=$(grep "^$f " $S | awk '{print $2}'); off=${off:-0}
    sz=$(stat -c %s $p)
    if [ $sz -gt $off ]; then
      new=$(tail -c +$((off+1)) $p | grep -E "$pat")
      sed -i "/^$f /d" $S; echo "$f $sz" >> $S
      [ -n "$new" ] && { echo "$new"; exit 0; }
    fi
  done
  pgrep -f gate_wave.sh >/dev/null || pgrep -f recorder.sh >/dev/null || { echo "no gate_wave/recorder running"; exit 0; }
  sleep 20
done
