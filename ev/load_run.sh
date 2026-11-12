#!/usr/bin/env bash
# 12 CPU hogs on 4 cores; phase 1: three loops in parallel, each 6x (asis, nopf), nested rows skipped; phase 2: one loop, 8x asis.
for i in $(seq 12); do timeout 1500 sh -c 'while :; do :; done' & done
sleep 20
for l in a b c; do ( for i in 1 2 3 4 5 6; do NESTED=1 bash /tmp/tmp.DtCQqRaCHl/ev/reviewer_driver.sh /tmp/tmp.DtCQqRaCHl/wt /tmp/tmp.DtCQqRaCHl/drv asis p1$l$i; NESTED=1 bash /tmp/tmp.DtCQqRaCHl/ev/reviewer_driver.sh /tmp/tmp.DtCQqRaCHl/wt /tmp/tmp.DtCQqRaCHl/drv nopf p1$l$i; done ) & lp="$lp $!"; done
wait $lp
echo PHASE2
for i in 1 2 3 4 5 6 7 8; do NESTED=1 bash /tmp/tmp.DtCQqRaCHl/ev/reviewer_driver.sh /tmp/tmp.DtCQqRaCHl/wt /tmp/tmp.DtCQqRaCHl/drv asis p2s$i; done
echo DONE
pkill -P $$ timeout
