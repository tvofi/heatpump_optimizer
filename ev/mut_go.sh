runsed() { name=$1; expr=$2
  sed -i "$expr" $F
  echo "$name edit: $(git diff -U0 -- $F | grep '^[-+] ' | tr '\n' '|')" >> $out
  node tests/card.mjs > $W/ev/mut_$name.log 2>&1; rc=$?
  fails=$(grep -c '^FAIL' $W/ev/mut_$name.log)
  first=$(grep -m3 '^FAIL' $W/ev/mut_$name.log | tr '\n' '|')
  if [ $rc -eq 0 ]; then v=SURVIVED; else v=KILLED; fi
  echo "$name: $v rc=$rc fails=$fails first=$first" >> $out
  git checkout -q -- $F; }
runsed NULL '15670s|$| // null|'
runsed R1 '15227a\    this._folds = { narrative: false, whynow: false };'
runsed M4 '15670d'
runsed M2 '15667d'
