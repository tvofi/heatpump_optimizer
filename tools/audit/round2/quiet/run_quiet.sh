#!/usr/bin/env bash
# Quiet-window wrapper: run one harness exactly as its header says, from the
# directory it was written in, with the thread pin and PYTHONPATH=tests/hastub,
# and record load1 before and after around the log.
#
#   run_quiet.sh <name> <dir> <command...>
#
# Writes tools/audit/round2/quiet/<name>.log (this directory) with a header
# line QUIET_LOAD_BEFORE, the harness output, and a footer QUIET_LOAD_AFTER,
# QUIET_EXIT and QUIET_WALL_S.
set -u
QDIR="$(cd "$(dirname "$0")" && pwd)"
name="$1"; dir="$2"; shift 2
LOG="$QDIR/$name.log"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export PYTHONPATH=tests/hastub
cd "$dir" || { echo "QUIET_EXIT=2 (no dir $dir)" | tee "$LOG"; exit 2; }
{
  echo "QUIET_NAME=$name"
  echo "QUIET_DIR=$dir"
  echo "QUIET_CMD=$*"
  echo "QUIET_START=$(date '+%Y-%m-%d %H:%M:%S')"
  echo "QUIET_LOAD_BEFORE=$(sysctl -n vm.loadavg)"
  echo "QUIET_CPU_BEFORE=$(top -l 2 -s 1 -n 0 2>/dev/null | grep 'CPU usage' | tail -1)"
} > "$LOG"
t0=$(date +%s)
"$@" >> "$LOG" 2>&1
rc=$?
t1=$(date +%s)
{
  echo "QUIET_LOAD_AFTER=$(sysctl -n vm.loadavg)"
  echo "QUIET_CPU_AFTER=$(top -l 2 -s 1 -n 0 2>/dev/null | grep 'CPU usage' | tail -1)"
  echo "QUIET_EXIT=$rc"
  echo "QUIET_WALL_S=$((t1-t0))"
  echo "QUIET_END=$(date '+%Y-%m-%d %H:%M:%S')"
} >> "$LOG"
echo "DONE $name exit=$rc wall=$((t1-t0))s load_after=$(sysctl -n vm.loadavg)"
exit $rc
