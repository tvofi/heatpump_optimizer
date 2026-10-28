#!/bin/zsh
E=/Users/timmalmstrom/hpo-seats/r10s6/rev-r5/2873/ev
for n in NULL N1_over_age_exception_off N1b_outranks_empty N4_reader_precedence_off N5_reader_always_overwrites N2_stale_never_promoted N3_age_not_rebased; do
  python3 $E/mutants_r4.py $E/arch $E/n $n tests/debug_collect.py > $E/n/$n.result 2>&1 &
done
wait
for n in NULL N4_reader_precedence_off N5_reader_always_overwrites; do
  python3 $E/mutants_r4.py $E/arch $E/n $n tests/features.py > $E/n/$n.features.result 2>&1 &
done
wait; cat $E/n/*.result > $E/mutants_r4-results.txt
