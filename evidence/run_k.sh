#!/bin/zsh
E=/Users/timmalmstrom/hpo-seats/r10s6/rev-r5/2873/ev
for n in NULL K1_implausible_unworded K2_sv_p_implausible_deleted K3_en_p_implausible_deleted K4_stale_unworded K5_sv_health_stale_deleted K6_table_names_unpublished_class K7_sv_p_implausible_blank; do
  python3 $E/kmutants_r5.py $E/arch $E/kmut $n > $E/kmut/$n.result 2>&1 &
done
wait; cat $E/kmut/*.result > $E/kmutants.txt
