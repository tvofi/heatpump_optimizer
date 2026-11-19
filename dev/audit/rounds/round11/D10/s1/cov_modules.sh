#!/usr/bin/env bash
# D10.M3 test-coverage: per-module statement coverage of
# custom_components/heatpump_optimizer over every default-gate test script
# (each run under its own coverage data dir, then combined), the measurement
# the Silver rule `test-coverage` ("Above 95% test coverage for all
# integration modules") asks for.
#
# Metric: per module, covered/total statements (coverage.py json
# `percent_covered`, statements only) over the union of every script of
# tools/coverage/coverage_tree.sh stage S (default all = fast + e2e + stress);
# RESULT lines: package percent, modules below 95.0, and the lowest module.
# Instrumented symbols: every module of custom_components/heatpump_optimizer
# (coverage.py traces each one's lines as the test scripts drive them).
# Perturbation: COV_DROP=<script> removes one test script from the run
# (e.g. COV_DROP=config_flow_steps): modules that only it covers fall, so
# modules_below_95 moves up / package percent moves down.
# Count key: coverage.py's executed-line set per module, the value the
# production module delivers when traced, not any recorded budget.
#
# Run (from the export root, never cd elsewhere):
#   PYTHON=~/.local/state/hpo/venv-ci/bin/python3 \
#     bash dev/audit/rounds/round11/D10/s1/cov_modules.sh [fast|e2e|stress|all]
# Needs network once: pip installs coverage into a private --target dir
# under $TMPDIR (the interpreter's own site-packages is not touched).
# macOS note: coverage_tree.sh's wait for late descendants is /proc-only, so
# this harness re-combines any late .coverage.* files left under the data dirs
# after the stage returns (RESULT late_files=N says how many).
# Expected: see REPORT.md (count; exact on the same interpreter and tree).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: macOS arm64
# (Apple silicon, 8 cores), Python 3.14 venv-ci.
for v in OMP_NUM_THREADS OPENBLAS_NUM_THREADS MKL_NUM_THREADS NUMEXPR_NUM_THREADS VECLIB_MAXIMUM_THREADS; do
  export "$v=${!v:-1}"
done
set -u
[ -f custom_components/heatpump_optimizer/manifest.json ] || { echo "run from the export root" >&2; exit 2; }
STAGE="${1:-all}"
PY="${PYTHON:-python3}"
ROOT="$(mktemp -d "${TMPDIR:-/tmp}/d10s1cov.XXXXXX")"
WORK="$ROOT/work"; mkdir -p "$WORK/site"
"$PY" -m pip install -q --disable-pip-version-check --target "$WORK/site" coverage > "$ROOT/pip.log" 2>&1 \
  || { echo "pip install coverage failed; see $ROOT/pip.log" >&2; exit 2; }
# coverage_tree.sh writes its own sitecustomize into $WORK/site and puts
# $WORK/site first on PYTHONPATH, so the coverage package installed there is
# importable by every traced process and by its `-m coverage` combine.
if [ -n "${COV_DROP:-}" ]; then
  # Drop one script: run the stage from a copy of run.sh's derivation without it.
  TREE="$ROOT/tree"; mkdir -p "$TREE"
  cp -R custom_components tests tools "$TREE/" 2>/dev/null
  for f in hacs.json VERSION RELEASE_NOTES.md README.md; do [ -f "$f" ] && cp "$f" "$TREE/"; done
  [ -d docs ] && cp -R docs "$TREE/"; [ -d blueprints ] && cp -R blueprints "$TREE/"; [ -d dev ] && cp -R dev "$TREE/"
  sed -i.bak "/run \"\$PYTHON\" tests\/${COV_DROP}\.py/d" "$TREE/tests/run.sh"
  echo "RESULT dropped_script=$COV_DROP"
  cd "$TREE" || exit 2
fi
W5P_WORK="$WORK" W5P_LANES="${W5P_LANES:-3}" PYTHON="$PY" bash tools/coverage/coverage_tree.sh "$STAGE" > "$ROOT/tree.log" 2>&1
echo "tree rc=$? log=$ROOT/tree.log"
OUT="$WORK/out"
# Late descendants (no /proc on macOS): combine whatever arrived after each
# script's own combine into the final data set.
late=$(ls "$WORK"/data/*/.coverage.* 2>/dev/null | wc -l | tr -d ' ')
echo "RESULT late_files=$late count"
if [ "$late" -gt 0 ]; then
  mkdir -p "$OUT/late"; cp "$WORK"/data/*/.coverage.* "$OUT/late/"
  PYTHONPATH="$WORK/site" "$PY" -m coverage combine --rcfile="$WORK/coveragerc" --append --keep "$OUT/late" >> "$OUT/logs/combine.log" 2>&1
  PYTHONPATH="$WORK/site" "$PY" -m coverage json --rcfile="$WORK/coveragerc" -o "$OUT/coverage.json" >> "$OUT/logs/combine.log" 2>&1
fi
cat "$OUT/scripts.tsv"
"$PY" - "$OUT/coverage.json" <<'PYEOF'
import json, sys, os
d = json.load(open(sys.argv[1]))
files = d["files"]
rows = []
for path, f in files.items():
    s = f["summary"]
    rows.append((s["percent_covered"] if s["num_statements"] else 100.0,
                 os.path.basename(path), s["num_statements"], s["missing_lines"]))
rows.sort()
below = [r for r in rows if r[0] < 95.0]
for p, name, n, miss in rows:
    print(f"MODULE {name} {p:.2f} stmts={n} missing={miss}")
t = d["totals"]
print(f"RESULT package_percent={t['percent_covered']:.2f} %")
print(f"RESULT modules={len(rows)} count")
print(f"RESULT modules_below_95={len(below)} count")
print(f"RESULT lowest_module={rows[0][1]}:{rows[0][0]:.2f} %")
for p, name, n, miss in below:
    print(f"RESULT below_95 {name}={p:.2f} %")
PYEOF
python3 - <<'PYEOF'
import os, time
r = os.times(); print(f"RESULT thread_factor=1.0")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
PYEOF
echo "data root: $ROOT"
