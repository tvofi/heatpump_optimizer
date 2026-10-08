#!/bin/bash
set -u
cd /Users/timmalmstrom/hpo-seats/review-2060/wt
PY=~/.local/state/hpo/venv-ci/bin/python
E=/Users/timmalmstrom/hpo-seats/review-2060/evidence
run() { echo "== $1"; PYTHONPATH=tests/hastub $PY tests/entities.py > $E/entities-$1.log 2>&1; echo "rc=$?"; grep -E "ENTITY CHECKS|^FAIL" $E/entities-$1.log | cut -c1-400; }
run head
# mutant: disable the root-as-shard arm
sed -i '' 's/shards = \[r\] if (r \/ "status").is_file() else/shards = [r] if False else/' tests/mutation_table.py
git diff --stat; run mutant
git checkout -- tests/mutation_table.py
# failing-test-first: main's merge_pin_shards under the branch's test
git show dcc77dd0:tests/mutation_table.py > tests/mutation_table.py
git diff --stat; run base-impl
git checkout -- tests/mutation_table.py
git status --short
