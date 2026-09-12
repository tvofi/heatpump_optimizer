#!/usr/bin/env bash
# D10 test-coverage (Silver) — package statement coverage of
# custom_components/heatpump_optimizer over the default-gate Python scripts.
#
# METRIC: covered statements / total statements of the integration package,
#         measured by coverage.py 7.16.0 over the scripts tests/run.sh runs
#         (one `coverage run` per script, combined), reported per module.
#
# RUN (from the export root):
#   D10_WORK=$(mktemp -d /private/tmp/hpo-d10-covXXXX) \
#   tools/audit/round4/D10/coverage_measure.sh fast
#   ... then the same with `e2e` to add the four end-to-end scripts.
#
# EXPECTED: package percent >= 95.0 is what the Silver rule asks for;
#           tests/coverage_budgets.json records 96.0 floor / 97.2 measured.
#           Tolerance +/- 0.3 pp (script set and coverage version dependent).
# BASELINE: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
# MACHINE:  8-core Apple M1, 8 GB, macOS 25.6.0, Python 3.11.5
#
# This wraps tools/audit/w5-partition/coverage_tree.sh rather than
# re-implementing it: the ratchet in tests/coverage_ratchet.py consumes that
# instrument's coverage.json, so measuring with a second implementation would
# not be comparable to the number the tree records.
set -u
[ -f custom_components/heatpump_optimizer/manifest.json ] || { echo "run from the export root" >&2; exit 2; }
STAGE="${1:-fast}"
WORK="${D10_WORK:?set D10_WORK to a private mktemp -d}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export PYTHON="${PYTHON:-/Library/Frameworks/Python.framework/Versions/3.11/bin/python3}"
export W5P_WORK="$WORK" W5P_OUT="$WORK/out"
tools/audit/w5-partition/coverage_tree.sh "$STAGE"
echo "RESULT load1=$(uptime | sed 's/.*load averages*: //' | awk '{print $1}')"
