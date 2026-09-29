#!/bin/bash
# usage: run_one.sh <perturbation-script-basename-without-.py>
# Resets wt-p to baseline, applies the script, checks it parses/imports and has no new ruff F-errors, measures.
set -e
A=$(cd "$(dirname "$0")" && pwd)
P=$1
WT=$A/wt-p
BASE=7952d8f9
if [ ! -d $WT ]; then git -C /home/user/heatpump_optimizer worktree add --detach $WT $BASE >/dev/null 2>&1; fi
git -C $WT checkout -q -f $BASE
git -C $WT clean -qfdx custom_components tests >/dev/null
python3 $A/perturb/$P.py $WT
cd $WT
CHANGED=$(git status --porcelain | awk '{print $2}' | grep '\.py$' || true)
for f in $CHANGED; do python3 -m py_compile $f; done
# new ruff F-findings only (baseline has some)
NEWF=$(ruff check --no-cache --select F --output-format concise $CHANGED 2>/dev/null | grep -v "^Found\|fixable\|^$" | sed 's/:[0-9]*:[0-9]*:/:/' | sort > /tmp/.rf_new.$$; git stash -q; ruff check --no-cache --select F --output-format concise $CHANGED 2>/dev/null | grep -v "^Found\|fixable\|^$" | sed 's/:[0-9]*:[0-9]*:/:/' | sort > /tmp/.rf_old.$$ || true; git stash pop -q; comm -13 /tmp/.rf_old.$$ /tmp/.rf_new.$$; rm -f /tmp/.rf_*.$$)
IMPORT=$(python3 -c "
import sys,importlib,pathlib; sys.path.insert(0,'tests/hastub'); sys.path.insert(0,'.')
for p in sorted(pathlib.Path('custom_components/heatpump_optimizer').glob('*.py')):
    importlib.import_module('custom_components.heatpump_optimizer.'+p.stem if p.stem!='__init__' else 'custom_components.heatpump_optimizer')
print('import-ok')" 2>&1 | tail -1)
python3 $A/measure.py $WT > $A/out/$P.json
git diff --stat | tail -1 > $A/out/$P.diffstat
git status --porcelain | grep '^??' >> $A/out/$P.diffstat || true
git diff > $A/out/$P.diff; for f in $(git status --porcelain | grep '^??' | awk '{print $2}'); do git diff --no-index /dev/null $f >> $A/out/$P.diff || true; done
echo "$NEWF" > $A/out/$P.newF
NF=$(echo -n "$NEWF" | grep -c . || true)
echo "$P | $IMPORT | new ruff F findings: $NF $(echo "$NEWF" | head -2 | cut -c1-120 | tr "\n" ";") | $(cat $A/out/$P.diffstat | head -1)"
