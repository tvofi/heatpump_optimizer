cd /home/user/heatpump_optimizer
W=$(cat $HOME/W.txt)
for i in $(seq 1 130); do
  python3 tools/audit/seat/merge_train.py classify 9394a6528c7683f5b8b5fb19a1d939e244c515e6 --pr 3442 > $W/ev/classify.txt 2>&1; rc=$?
  echo "$(date -u +%T) rc=$rc $(tail -1 $W/ev/classify.txt)" >> $W/ev/classify.log
  [ $rc -ne 3 ] && echo "CLASSIFY-DONE rc=$rc" && exit 0
  sleep 70
done
echo "CLASSIFY-TIMEOUT"
