cd /home/user/rev
for i in $(seq 1 20); do
  python3 tools/audit/seat/merge_train.py classify c7c5cef52a49bed59ee4c8a42e495ef2dae30db5 --pr 3265 > /home/user/cl.out 2>&1; rc=$?
  echo "$(date -u +%FT%TZ) rc=$rc $(tail -1 /home/user/cl.out)" >> /tmp/tmp.IB3Jmm0wYW/ev/classify-history.txt
  [ $rc -eq 0 ] && { cp /home/user/cl.out /tmp/tmp.IB3Jmm0wYW/ev/classify.txt; echo GREEN; exit 0; }
  sleep 120
done
cp /home/user/cl.out /tmp/tmp.IB3Jmm0wYW/ev/classify.txt; echo STILL-RED
