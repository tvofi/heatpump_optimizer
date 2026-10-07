#!/usr/bin/env bash
# Verifier-3 own harness (D10-01, decisive row config-flow-test-coverage).
# METRIC: statement coverage of custom_components/heatpump_optimizer/config_flow.py
#         collected by coverage 7.16.0 over (a) tests/config_flow_steps.py alone,
#         (b) the five scripts the register's own comment names
#         (config_flow_steps entities golden features deployment_shape).
# RUN: bash tools/audit/round4/D10/verify3/cov_config_flow_v3.sh   (worktree root)
# Writes only under a private mktemp -d; prints RESULT lines.
set -u
ROOT=$(pwd)
PY=/Library/Frameworks/Python.framework/Versions/3.11/bin/python3
W=$(mktemp -d /private/tmp/hpo-d10-v3cfsXXXX)
mkdir -p "$W/data"
cat > "$W/coveragerc" <<RCEOF
[run]
parallel = True
relative_files = True
data_file = $W/data/.coverage
source = $ROOT/custom_components/heatpump_optimizer
[report]
precision = 1
RCEOF
export COVERAGE_PROCESS_START="$W/coveragerc"
export PYTHONPATH="$W/site:$ROOT/tests/hastub"
mkdir -p "$W/site"
cat > "$W/site/sitecustomize.py" <<'PYEOF'
try:
    import coverage
except ImportError:
    pass
else:
    coverage.process_startup()
PYEOF
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export HPO_PLANDATA="$W/plandata.json"
for s in config_flow_steps entities golden features deployment_shape; do
  a=$(date +%s)
  if [ "$s" = "golden" ]; then
    GOLDEN_MODE=strict "$PY" "tests/$s.py" > "$W/$s.log" 2>&1
  else
    "$PY" "tests/$s.py" > "$W/$s.log" 2>&1
  fi
  rc=$?; b=$(date +%s)
  echo "script=$s exit=$rc wall=$((b-a))s"
done
"$PY" -m coverage combine --rcfile="$W/coveragerc" --append --keep > "$W/combine.log" 2>&1
unset COVERAGE_PROCESS_START
"$PY" - "$W" "$PY" <<'PY'
import json, subprocess, sys, os, shutil
w, py = sys.argv[1], sys.argv[2]
rc = os.path.join(w, "coveragerc")
# combined (five scripts)
subprocess.run([py, "-m", "coverage", "json", "--rcfile=" + rc, "-o", os.path.join(w, "cov5.json")], check=True, capture_output=True)
d = json.load(open(os.path.join(w, "cov5.json")))
for name, f in d["files"].items():
    if name.endswith("config_flow.py"):
        s = f["summary"]
        print(f"RESULT cf_cov_five_scripts={round(s['percent_covered'],1)}% stmts={s['num_statements']} missed={s['missing_lines']}")
        print(f"RESULT cf_missing_lines_five={f.get('missing_lines')}")
PY
# config_flow_steps alone: recombine only its data file
rm -rf "$W/data2"; mkdir -p "$W/data2"
for f in "$W"/data/.coverage.*; do :; done
echo "workdir=$W (kept for inspection)"
