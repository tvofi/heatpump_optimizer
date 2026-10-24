# rev.sh <pr> <branch>  : dispatch reviewer at origin/<branch> head, publish, rpool
set -e
export PATH=/Users/timmalmstrom/hpo-seats/r10s6/orch-wt/tools/audit/seat/shims:$PATH
cd /Users/timmalmstrom/hpo-seats/r10s6/orch-wt
pr=$1; br=$2; git fetch -q origin; H=$(git rev-parse origin/$br)
bash tools/pr/approve_held_runs.sh tvofi/heatpump_optimizer $br 2>&1 | tail -1 | cut -c1-150
out=$(bash tools/audit/seat/bus.sh dispatch $pr $H pool 2>&1); echo "$out" | tail -2 | cut -c1-200
N=$(echo "$out" | grep -oE '[0-9a-f]{32}' | tail -1); [ -n "$N" ] || { echo "NO NONCE"; exit 1; }
n8=${N:0:8}; ref=dispatch/reviewer-$pr-$n8
python3 tools/audit/seat/cloud_dispatch.py --role reviewer --overlay /Users/timmalmstrom/hpo-orch/r10s6/cloud-overlay.json --topic $pr-$n8 --model claude-opus-5-5 --head $H --pr $pr --nonce $N ${BRIEF:+--brief $BRIEF} --out /Users/timmalmstrom/hpo-orch/r10s6/payloads/rev-$pr-$n8.json >/dev/null
PYTHONPATH=tools/audit/seat python3 - <<PY
import json,sys,importlib.util
spec=importlib.util.spec_from_file_location("cd","tools/audit/seat/cloud_dispatch.py");cd=importlib.util.module_from_spec(spec);sys.modules["cd"]=cd;spec.loader.exec_module(cd)
p=json.load(open("/Users/timmalmstrom/hpo-orch/r10s6/payloads/rev-$pr-$n8.json"))
cd._publish(".","$ref",{"PAYLOAD.json":json.dumps(p),"PROMPT.md":p["job_config"]["ccr"]["events"][0]["data"]["message"]["content"]})
PY
old=$(git show origin/dispatch/rpool-s6:POOL.txt | grep "dispatch/reviewer-$pr-" | tr '\n' ' ')
python3 /Users/timmalmstrom/hpo-orch/r10s6/scratch/pool.py rpool-s6 $ref $old
git fetch -q origin; git show origin/dispatch/rpool-s6:POOL.txt | grep -q "$ref" && echo "fire-owed-pool #$pr $H $N $ref (pool read back OK)" | tee -a /Users/timmalmstrom/hpo-orch/r10s6/dispatch-report.txt
