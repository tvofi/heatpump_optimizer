W=$1; i=$2; shift 2
for n in "$@"; do
  cd $W/wt$i && git checkout -q -- tools/audit/seat/merge_train.py
  python3 $W/mutants.py $n tools/audit/seat/merge_train.py || { echo "== $n APPLY-FAILED" >> $W/ev/mut-$i.txt; continue; }
  { echo "== $n"; python3 tools/audit/seat/merge_train.py --self-test 2>&1 | grep -E '^  FAIL|self-test:'; echo "rc=${PIPESTATUS[0]}"; } >> $W/ev/mut-$i.txt
  git checkout -q -- tools/audit/seat/merge_train.py
done
echo DONE >> $W/ev/mut-$i.txt
