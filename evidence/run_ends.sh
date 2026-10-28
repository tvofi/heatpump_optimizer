#!/bin/zsh
E=/Users/timmalmstrom/hpo-seats/r10s6/rev-r5/2873/ev
export NODE_OPTIONS=--max-old-space-size=8192
for tag dir in tf /Users/timmalmstrom/hpo-seats/r10s6/rev-2873-r5-tf head /Users/timmalmstrom/hpo-seats/r10s6/rev-2873-r5; do

  ( cd $dir && PYTHONPATH=tests/hastub python3 tests/plan_view.py > $E/plan_view-$tag.txt 2>&1 && node tests/card.mjs > $E/card-$tag.txt 2>&1; echo "rc=$?" >> $E/card-$tag.txt ) &
done
wait
