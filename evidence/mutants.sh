#!/bin/bash
# usage: mutants.sh W ; each mutant: name|line|python-replace-from|to
W=$1; F=custom_components/heatpump_optimizer/legionella.py
run() { name=$1; ln=$2; from=$3; to=$4
  d=$W/mut-$name; rm -rf $d; mkdir -p $d; (cd $W/head && git archive HEAD) | tar -x -C $d
  python3 - "$d/$F" "$ln" "$from" "$to" <<'PY'
import sys
p,ln,a,b=sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4]
L=open(p).read().split("\n"); s=L[ln-1]
assert a in s,(ln,s); L[ln-1]=s.replace(a,b,1); open(p,"w").write("\n".join(L))
PY
  (cd $d && f=$(PYTHONPATH=tests/hastub timeout 1500 python3 tests/features.py 2>&1); g=$(PYTHONPATH=tests/hastub python3 tests/guard_pins.py 2>&1)
   echo "MUTANT $name: features: $(echo "$f" | tail -1) | guard_pins: $(echo "$g" | tail -1)"; echo "$f" | grep -E "^\s*(FAIL|✗|x )" | head -5; echo "$g" | grep -E "FAIL" | head -3) > $W/ev/mutant_$name.txt 2>&1
  rm -rf $d
}
run M1_retry 628 "return min(interval_h, DHW_LEGIONELLA_RETRY_HOURS) if self._has_probe() else interval_h" "return interval_h" &
run M2_overdue_observe 484 "self.check_overdue()" "pass" &
run M4_fold 344 "if pending is not None and (" "if False and (" &
run M5_overdue_track 247 "self.check_overdue()" "pass" &
wait
run R1_cap_drop 613 "min(since, age)" "age" &
run R2_pending_ignores_completion 621 "utc_elapsed_seconds(attempt, last) <= 0" "False" &
run R3_watched_ignores_enabled 655 "params.dhw_enabled and params.dhw_legionella_enabled" "True" &
run R4_overdue_bound 60 "age_h > interval_days * 24.0" "age_h > interval_days * 48.0" &
wait
cat $W/ev/mutant_*.txt
