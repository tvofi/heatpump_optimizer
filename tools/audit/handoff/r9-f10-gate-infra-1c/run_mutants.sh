#!/usr/bin/env bash
# usage: run_mutants.sh <tree-root> <mutant>...
# <tree-root> holds tests/ and custom_components/ (the repo root, or a git-archive export).
# Each mutant (NONE, an RCA-BULK-1 p7_mutants.py name, or a FIX-* line of #1756's fix) is
# applied to a scratch copy, tests/dst_checks.py runs there, and its FAIL lines print.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
SRC=$1; shift
for m in "$@"; do
  D=$(mktemp -d)
  cp -r "$SRC/tests" "$SRC/custom_components" "$D/"
  find "$D" -name __pycache__ -prune -exec rm -rf {} +
  if [ "$m" != "NONE" ]; then
    case "$m" in
      FIX-*) python3 "$HERE/fix_mutants.py" "$D" "$m" || { echo "== $m: mutant did not apply"; rm -rf "$D"; continue; } ;;
      *) python3 "$HERE/p7_mutants.py" "$D" "$m" >/dev/null || { echo "== $m: mutant did not apply"; rm -rf "$D"; continue; } ;;
    esac
  fi
  (cd "$D" && HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub:tests:custom_components OPENBLAS_CORETYPE=Haswell python3 tests/dst_checks.py > out.log 2>&1; echo "rc=$?" >> out.log)
  echo "== $m: $(tail -1 "$D/out.log") $(grep -c '^  FAIL' "$D/out.log") FAIL lines"
  grep '^  FAIL' "$D/out.log" | cut -c1-170
  rm -rf "$D"
done
