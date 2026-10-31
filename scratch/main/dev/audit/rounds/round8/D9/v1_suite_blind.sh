#!/usr/bin/env bash
# D9 round 8 verifier v1 -- does ANY script the scoped gate selects for coordinator.py notice a
# one-line production mutation that doubles the per-cycle _build_data_dict work?
#
# Metric (v1, one line): number of Python gate scripts selected by `tests/closure.py select
#   --files custom_components/heatpump_optimizer/coordinator.py` whose exit status or FAIL-line set differs
#   between an unmutated copy of this tree and a copy carrying the mutation below.
# Mutation (custom_components/heatpump_optimizer/coordinator.py:4569, the success return of
#   _async_update_data):  return self._build_data_dict()
#                   ->    return [self._build_data_dict() for _i in (0, 1)][-1]      (default)
#   or with --tuple  ->    return (self._build_data_dict(), self._build_data_dict())[1]
#   The --tuple spelling adds a second call SITE, which tests/structure.py's call-edge ratchet
#   counts (internal_call_edges/cross_seam_edges/cut_views +1): the ratchet sees the syntax,
#   not the cost. The default spelling doubles the same work with no new call site.
# Copies (no .git, so env_drift.py and the Node card scripts are not run; the mutation changes
#   no published value, which is all they compare) live under /home/claude/audit-r8/tmp/D9-v1/.
# Command (repo root): bash tools/audit/round8/D9/v1_suite_blind.sh [--tuple]
# Expected: 0 scripts change status with the default spelling; 1 (structure.py) with --tuple (exact). Baseline cdf82daa; 4-vCPU shared container.
set -u
ROOT=$(pwd)
T=/home/claude/audit-r8/tmp/D9-v1
export TMPDIR=$T HPO_PLANDATA=$T/plandata PYTHONPATH=tests/hastub PYTHONHASHSEED=0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
mk() {  # $1 = dir
  rm -rf "$1"; mkdir -p "$1"
  tar --exclude=.git --exclude=tools/audit/round8 -C "$ROOT" -cf - . | tar -xf - -C "$1"
}
mk "$T/base_tree"; mk "$T/mut_tree"
F=custom_components/heatpump_optimizer/coordinator.py
grep -qx '            return self._build_data_dict()' <(sed -n 4569p "$T/mut_tree/$F") || { echo "anchor moved"; exit 2; }
if [ "${1:-}" = "--tuple" ]; then
  sed -i '4569s/.*/            return (self._build_data_dict(), self._build_data_dict())[1]/' "$T/mut_tree/$F"
else
  sed -i '4569s/.*/            return [self._build_data_dict() for _i in (0, 1)][-1]/' "$T/mut_tree/$F"
fi
sed -n 4569p "$T/mut_tree/$F"
SCRIPTS="config_flow_steps deployment_shape doc_claims entities features finite_boundary golden manual_plan plan_view solar_alignment structure typing_ruler wood_advisor"
changed=0; ran=0
for s in $SCRIPTS; do
  (cd "$T/base_tree" && timeout 1800 python3 "tests/$s.py" > "$T/base_$s.log" 2>&1); rb=$?
  (cd "$T/mut_tree" && timeout 1800 python3 "tests/$s.py" > "$T/mut_$s.log" 2>&1); rm_=$?
  ran=$((ran+1))
  # a script failing in both copies (no .git) still counts as changed if its FAIL lines differ
  fb=$(grep -E "FAIL|FAILED" "$T/base_$s.log" | sed -E 's/[0-9]+(\.[0-9]+)? ?(ms|s)\b//g; s#(base|mut)_tree#TREE#g' | sort | md5sum)
  fm=$(grep -E "FAIL|FAILED" "$T/mut_$s.log" | sed -E 's/[0-9]+(\.[0-9]+)? ?(ms|s)\b//g; s#(base|mut)_tree#TREE#g' | sort | md5sum)
  flag=""; if [ "$rb" != "$rm_" ] || [ "$fb" != "$fm" ]; then changed=$((changed+1)); flag="  <-- CHANGED"; fi
  echo "script tests/$s.py base_rc=$rb mut_rc=$rm_$flag"
done
echo "RESULT scripts_run=$ran count"
echo "RESULT scripts_changing_status_under_2x_build=$changed count"
echo "RESULT thread_factor=1.000 (no timed work)"
echo "RESULT load1=$(cut -d' ' -f1 /proc/loadavg)"
echo "RESULT swapins=$(awk '/^pswpin/{print $2}' /proc/vmstat)"
