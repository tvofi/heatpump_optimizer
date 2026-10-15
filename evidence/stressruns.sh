#!/bin/bash
# reviewer's solve-CPU channel runs, each under the gate lease (auto-lease, label revi1)
S=/private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad
cd $S/revi1 && export PATH=$PWD/tools/audit/seat/shims:$PATH
for f in "$@"; do
  n=$(ls $S/rev/sc-*.log 2>/dev/null | wc -l | tr -d ' ')
  log=$S/rev/sc-$n-f$f.log
  echo "START factor=$f load1=$(sysctl -n vm.loadavg | awk '{print $2}') $(date -u +%H:%M:%SZ)" > $log
  PYTHONPATH=tests/hastub seat-python3 tests/gate_lock.py auto-lease --label revi1 -- \
    seat-python3 $S/rev/tf.py dev/audit/harnesses/r10_i1_solve_cpu_2x.py --factor $f --ref 5603ee319 >> $log 2>&1
  echo "END rc=$? $(date -u +%H:%M:%SZ)" >> $log
  echo "factor=$f $(grep -h RESULT $log | grep -E 'flagged|median|judged|count_or|load1|thread' | tr '\n' ' ')" >> $S/rev/sc.out
done
echo ALLDONE >> $S/rev/sc.out
