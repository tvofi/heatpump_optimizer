cd /home/user/heatpump_optimizer
while :; do python3 tools/audit/seat/merge_train.py classify f6d7be0cd4ef22a353d72532ca18aae38089e5cc --pr 3327 > $1/ev/classify.txt 2>&1; rc=$?; echo "rc=$rc $(date -u +%T)" >> $1/ev/classify_rc.txt; [ $rc != 3 ] && exit $rc; sleep 240; done
