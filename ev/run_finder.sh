#!/bin/bash
# run finder's harnesses at one end; $1 = base|head
d=/tmp/seat/rev2391/$1; out=/tmp/seat/rev2391/ev/$1; mkdir -p $out; cd $d
for P in P0 P1; do for G in 0.4 0.6 1.0; do
  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/study-ident/ident_rolling.py --plant $P --delivery $G > $out/ident_${P}_g$G.txt 2>&1; echo "rc=$?" >> $out/ident_${P}_g$G.txt
done; done
PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/study/learner_v2.py --two-zone > $out/learner_v2.txt 2>&1; echo "rc=$?" >> $out/learner_v2.txt
echo DONE > $out/finder.done
