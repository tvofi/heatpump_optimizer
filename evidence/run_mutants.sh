#!/bin/bash
cd /Users/timmalmstrom/hpo-seats/review-2025-r6/wt
E=/Users/timmalmstrom/hpo-seats/review-2025-r6/ev
PY=~/.local/state/hpo/venv-ci/bin/python
for m in "$@"; do
  git diff --quiet -- custom_components || { echo "DIRTY before $m"; exit 2; }
  python3 $E/mutate_r6.py $m > $E/ent_$m.txt 2>&1 || { echo "apply failed $m"; cat $E/ent_$m.txt; exit 3; }
  git diff -- custom_components >> $E/ent_$m.txt
  PYTHONPATH=tests/hastub $PY tests/entities.py >> $E/ent_$m.txt 2>&1
  rc=$?
  git checkout -q -- custom_components
  git diff --quiet -- custom_components || { echo "RESTORE FAILED $m"; exit 4; }
  echo "$m rc=$rc $(grep -cE '^  FAIL ' $E/ent_$m.txt) $(tail -1 $E/ent_$m.txt)"
done
echo DONE
