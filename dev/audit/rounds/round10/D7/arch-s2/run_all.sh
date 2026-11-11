#!/usr/bin/env bash
# Re-run harness.py for each named patch (default: every patch, then all together).
#   bash dev/audit/rounds/round10/D7/arch-s2/run_all.sh [NN_name ...]
# Logs go to a mktemp -d root printed first. Run from the repository root.
set -u
BASE=554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef
DIR=dev/audit/rounds/round10/D7/arch-s2
OUT=$(mktemp -d "${TMPDIR:-/tmp}/arch-s2-logs.XXXXXX")
echo "logs: $OUT"
if [ $# -eq 0 ]; then
  set -- $(cd "$DIR/patches" && ls *.patch | sed 's/\.patch$//')
fi
for n in "$@"; do
  PYTHONPATH=tests/hastub python3 "$DIR/harness.py" --base "$BASE" "$DIR/patches/$n.patch" > "$OUT/$n.log" 2>&1
  echo "rc=$?" >> "$OUT/$n.log"
  echo "== $n"; grep -E '^RESULT (delta_S|perturbed_delta_S|admissible|[a-z_]+=[0-9]+->)|^rc=' "$OUT/$n.log"
done
