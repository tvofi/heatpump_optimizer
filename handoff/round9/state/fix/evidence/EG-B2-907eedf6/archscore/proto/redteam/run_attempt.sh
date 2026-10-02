#!/bin/bash
# usage: run_attempt.sh attempts/NN_name.py   -> resets wt, applies, checks, scores
set -e
SCR=/tmp/claude-0/-home-user-heatpump-optimizer/1b5fa08f-9bd8-59e8-b197-ffb291fc579e/scratchpad/archscore
RT=$SCR/redteam; WT=${WT:-$RT/wt}
A=$(realpath "$1"); N=$(basename "$A" .py)
git -C "$WT" reset -q --hard 7952d8f9; git -C "$WT" clean -qfdx custom_components tests >/dev/null
python3 "$A" "$WT"
git -C "$WT" diff --stat | tail -3 > $RT/out/$N.diffstat
git -C "$WT" diff > $RT/out/$N.diff
python3 $RT/import_check.py "$WT"
cd $SCR/b
python3 measure_vec.py "$WT" > $RT/out/$N.vec.json
python3 metrics_v1.py "$WT" > $RT/out/$N.v1.json
python3 - "$RT/out/$N" <<'PY'
import json,sys
p=sys.argv[1];a=json.load(open(p+'.vec.json'));a.update(json.load(open(p+'.v1.json')));json.dump(a,open(p+'.json','w'),sort_keys=True)
errs=[k for k in a if 'error' in k]
if errs: print('METRIC ERRORS', {k:a[k] for k in errs})
PY
python3 arch_score.py --delta $RT/out/base.json $RT/out/$N.json | tee $RT/out/$N.delta.json
cat $RT/out/$N.diffstat
