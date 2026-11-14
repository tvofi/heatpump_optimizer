set -uo pipefail
for n in 8000 0; do h=$(printf 'aaaa\trefs/heads/x\n'; i=0; while [ $i -lt $n ]; do printf '%040d\trefs/heads/f%d\n' $i $i; i=$((i+1)); done)
 printf '%s\n' "$h" | grep -q '^aaaa[[:space:]]refs/heads/'; echo "lines=$((n+1)) pipe PIPESTATUS=${PIPESTATUS[*]}"
 grep -q '^aaaa[[:space:]]refs/heads/' <<<"$h"; echo "lines=$((n+1)) herestring rc=$?"; done
