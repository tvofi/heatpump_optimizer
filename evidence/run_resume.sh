#!/bin/zsh
# Resume after the 12:42Z reboot: the card arms and the features arms died.
E=/Users/timmalmstrom/hpo-seats/r10s6/rev-r5/2873/ev
export NODE_OPTIONS=--max-old-space-size=8192
( cd /Users/timmalmstrom/hpo-seats/r10s6/rev-2873-r5-tf && PYTHONPATH=tests/hastub python3 tests/plan_view.py > $E/plan_view-tf.txt 2>&1 && node tests/card.mjs > $E/card-tf.txt 2>&1; echo "rc=$?" >> $E/card-tf.txt ) &
( cd /Users/timmalmstrom/hpo-seats/r10s6/rev-2873-r5 && PYTHONPATH=tests/hastub python3 tests/plan_view.py > $E/plan_view-head.txt 2>&1 && node tests/card.mjs > $E/card-head.txt 2>&1; echo "rc=$?" >> $E/card-head.txt ) &
for n in NULL N4_reader_precedence_off N5_reader_always_overwrites; do
  python3 $E/mutants_r4.py $E/arch $E/n $n tests/features.py > $E/n/$n.features.result 2>&1 &
done
wait
for batch in "NULL K1_implausible_unworded K2_sv_p_implausible_deleted K3_en_p_implausible_deleted" "K4_stale_unworded K5_sv_health_stale_deleted K6_table_names_unpublished_class K7_sv_p_implausible_blank"; do
  for n in ${=batch}; do ARMS=card python3 $E/kmutants_r5.py $E/arch $E/kmut $n > $E/kmut/$n.card.result 2>&1 & done
  wait
done
echo resume-done
