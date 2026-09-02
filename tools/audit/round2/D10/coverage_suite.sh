#!/usr/bin/env bash
# D10 harness: test-coverage and config-flow-test-coverage (rules test-coverage, config-flow-test-coverage).
#
# Metric: statement coverage of custom_components/heatpump_optimizer/*.py (per module and total)
#         over the Python scripts of the default gate (tests/run.sh lanes, SLOW unset), measured by
#         coverage.py in EVERY process the scripts start (sitecustomize + COVERAGE_PROCESS_START, so
#         features.py's dst_checks.py subprocess is measured too), then combined.
# Command (from the export root):
#   PYTHON=/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/tvofi-claude/.venv/bin/python \
#   D10_COV_PREFIX=/tmp/d10-cov tools/audit/round2/D10/coverage_suite.sh
#   (D10_COV_PREFIX is a private prefix holding coverage.py: `pip install --target /tmp/d10-cov coverage`;
#    SLOW=1 adds tests/rolling.py, ~15 min uncovered.)
# Expected: RESULT coverage_total_pct within ±1.0 pt of the value in coverage/RESULTS.txt; the per-module
#           table in coverage/coverage_report.txt. Exact-count metric; wall seconds are PROVISIONAL
#           (shared box during the fan-out).
# Baseline: c398fc84eec25fc44b60d74aae05b9a2da205884. Machine: Apple M1, 8 GB, macOS (Darwin 25.6.0),
#           Python 3.13.1, coverage 7.16.0 (sysmon core).
# Writes only under tools/audit/round2/D10/coverage/ and a private temp root (HPO_PLANDATA is set there).
# Never takes /tmp/hpo-gate.lock: this is not the gate, it is a measurement of the gate's scripts.
set -u
if [ ! -f custom_components/heatpump_optimizer/manifest.json ]; then
  echo "run from the export root" >&2; exit 2
fi
# Thread pin (tests/stress.py lines 60-64), before any Python starts.
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}" OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}" NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-1}"
export VECLIB_MAXIMUM_THREADS="${VECLIB_MAXIMUM_THREADS:-1}"

PY="${PYTHON:-}"
if [ -z "$PY" ]; then
  if [ -x .venv/bin/python ]; then PY=.venv/bin/python; else PY=python3; fi
fi
COVPREFIX="${D10_COV_PREFIX:-/tmp/d10-cov}"
OUT="$PWD/tools/audit/round2/D10/coverage"
TMP=$(mktemp -d "${TMPDIR:-/tmp}/d10-cov-XXXXXX")
mkdir -p "$OUT/logs" "$TMP/site" "$TMP/data"
export HPO_PLANDATA="$TMP/plandata.json"

cat > "$TMP/site/sitecustomize.py" <<'PYEOF'
try:
    import coverage
except ImportError:  # a process without the private prefix on its path: measure nothing, break nothing
    pass
else:
    coverage.process_startup()
PYEOF
cat > "$TMP/coveragerc" <<RCEOF
[run]
parallel = True
relative_files = True
data_file = $TMP/data/.coverage
source = $PWD/custom_components/heatpump_optimizer
[report]
precision = 1
RCEOF
export COVERAGE_PROCESS_START="$TMP/coveragerc"
export PYTHONPATH="$COVPREFIX:$TMP/site:$PWD/tests/hastub"

if ! "$PY" -c "import coverage" 2>/dev/null; then
  echo "coverage not importable from $COVPREFIX" >&2; exit 2
fi

# The default gate's Python scripts, lane order (tests/run.sh): units, golden, e2e, then stress alone.
# env_drift.py and closure.py need git and are not run in a git-less export; the .mjs scripts are Node.
SCRIPTS="features entities manual_plan open_meteo solar_alignment golden validate edge backtest optimality plan_view frontend"
if [ "${SLOW:-0}" = "1" ]; then SCRIPTS="$SCRIPTS rolling"; fi
SCRIPTS="$SCRIPTS stress"

: > "$OUT/scripts.tsv"
echo -e "script\texit\twall_s" >> "$OUT/scripts.tsv"
t0=$(date +%s)
for s in $SCRIPTS; do
  a=$(date +%s)
  "$PY" "tests/$s.py" > "$OUT/logs/$s.log" 2>&1
  rc=$?
  b=$(date +%s)
  echo -e "$s\t$rc\t$((b-a))" >> "$OUT/scripts.tsv"
  echo "ran tests/$s.py exit=$rc wall=$((b-a))s"
done
t1=$(date +%s)

# Report from the export root: relative_files resolves paths against the cwd, so reporting from
# anywhere else fails with "No source for code". The RESULTS block below must not start a tracer
# of its own, hence the unset.
"$PY" -m coverage combine --rcfile="$TMP/coveragerc" --keep > "$OUT/logs/combine.log" 2>&1
unset COVERAGE_PROCESS_START
"$PY" -m coverage report --rcfile="$TMP/coveragerc" > "$OUT/coverage_report.txt" 2>&1
"$PY" -m coverage json --rcfile="$TMP/coveragerc" -o "$OUT/coverage.json" >> "$OUT/logs/combine.log" 2>&1

"$PY" - "$OUT" "$((t1-t0))" <<'PYEOF' | tee "$OUT/RESULTS.txt"
import json, os, sys, time
out, wall = sys.argv[1], int(sys.argv[2])
d = json.load(open(os.path.join(out, "coverage.json")))
files = {os.path.basename(k): v["summary"] for k, v in d["files"].items()}
tot = d["totals"]
print(f"RESULT coverage_total_pct={tot['percent_covered']:.1f} pct")
print(f"RESULT coverage_statements={tot['num_statements']} count")
print(f"RESULT coverage_missing={tot['missing_lines']} count")
cf = files.get("config_flow.py")
if cf: print(f"RESULT coverage_config_flow_pct={cf['percent_covered']:.1f} pct")
ge = sum(1 for v in files.values() if v["percent_covered"] >= 95.0)
print(f"RESULT coverage_modules_ge95={ge} of {len(files)} count")
rows = sorted(files.items(), key=lambda kv: kv[1]["percent_covered"])
with open(os.path.join(out, "per_module.tsv"), "w") as fh:
    fh.write("module\tstatements\tmissing\tpercent\n")
    for name, s in sorted(files.items()):
        fh.write(f"{name}\t{s['num_statements']}\t{s['missing_lines']}\t{s['percent_covered']:.1f}\n")
for name, s in rows[:12]:
    print(f"RESULT module_{name[:-3]}_pct={s['percent_covered']:.1f} pct")
scripts = [l.rstrip("\n").split("\t") for l in open(os.path.join(out, "scripts.tsv"))][1:]
failed = [s for s, rc, w in scripts if rc != "0"]
print(f"RESULT scripts_run={len(scripts)} count")
print(f"RESULT scripts_nonzero_exit={len(failed)} count  # {' '.join(failed)}")
print(f"RESULT wall_s={wall} s  # PROVISIONAL, shared box")
# contention markers (contract): thread factor over a pinned numpy matmul, load1, swapins
import numpy as np
a = np.random.default_rng(0).standard_normal((400, 400))
c0, t0 = time.process_time(), time.thread_time()
for _ in range(20): a @ a
c1, t1 = time.process_time(), time.thread_time()
print(f"RESULT thread_factor={(c1-c0)/max(t1-t0,1e-9):.2f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
swap = "n/a"
try:
    import subprocess
    vs = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
    for line in vs.splitlines():
        if line.startswith("Swapins"):
            swap = line.split(":")[1].strip().rstrip(".")
except Exception:
    pass
print(f"RESULT swapins={swap}")
PYEOF
echo "temp root kept for inspection: $TMP"
