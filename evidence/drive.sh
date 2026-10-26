#!/bin/bash
# usage: drive.sh <nightly.yml> ; extracts lines from "# THE BATCH" to the skip-batch-gate line, runs under runner bash -e
Y=$1
a=$(grep -n '# THE BATCH' "$Y" | cut -d: -f1); b=$(grep -n 'skip-batch-gate' "$Y" | head -1 | cut -d: -f1)
GATE=$(sed -n "${a},${b}p" "$Y")
mkdir -p stub; 
for rc in 4 0 1 2; do
  cat > stub/python3 <<S
#!/bin/sh
exit $rc
S
  chmod +x stub/python3
  f=$(mktemp); { echo "python3() { return $rc; }"; echo "set -uo pipefail"; echo 'status="skip-unknown"'; echo 'for try in 1 2 3; do'; echo "$GATE"; echo 'status="reached-apply"; break'; echo 'done'; echo 'echo "RECORD AUTOFIX: $status"'; } > $f
  RUNNER_TEMP=/nonexistent EVENT=push bash --noprofile --norc -eo pipefail $f > out.txt 2>&1; ec=$?
  echo "rc=$rc step_exit=$ec output=[$(tr '\n' ' ' < out.txt)]"
done
