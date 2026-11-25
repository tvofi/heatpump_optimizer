#!/usr/bin/env bash
# D5-s10 non-finding check: every example the header of .claude/hooks/pre-bash.sh names (lines 4-26: what it
# refuses, what stays allowed, what command position covers, the known gaps) driven through the real hook.
# Metric: RESULT mismatches = examples whose exit code differs from the header's statement (2 refuse, 0 allow).
# Command (export root): bash dev/audit/rounds/round11/D5/s10/pre_bash_claims.sh
# Expected at 92d38ecb (box B12, round 11): RESULT examples=21, RESULT mismatches=0, exact.
# Perturbation: HOOK=<a copy with `"pkill", "killall"` changed to `"killall"`> raises mismatches (up).
# Writes only under mktemp -d.
set -u
HOOK=${HOOK:-.claude/hooks/pre-bash.sh}
T=$(mktemp -d); (cd "$T" && git init -q -b feature)
n=0; bad=0
chk() { n=$((n+1))
  printf '%s' "$(python3 -c 'import json,sys;print(json.dumps({"tool_input":{"command":sys.argv[1]}}))' "$1")" \
    | CLAUDE_PROJECT_DIR=$T bash "$HOOK" >/dev/null 2>&1; rc=$?
  [ "$rc" = "$2" ] || { bad=$((bad+1)); echo "   MISMATCH rc=$rc want=$2 :: $1"; }; }
chk 'pkill -f foo' 2; chk 'killall foo' 2; chk 'pgrep x | xargs kill' 2; chk 'kill $(pgrep x)' 2
chk 'kill 1234' 0; chk 'kill $!' 0; chk 'kill $(cat run.pid)' 0
chk 'echo "never pkill"' 0; chk '# pkill x' 0; chk 'grep pkill file' 0; chk "$(printf 'cat <<EOF\npkill x\nEOF')" 0
chk "bash -c 'pkill x'" 2; chk "eval 'pkill x'" 2; chk 'sudo pkill x' 2; chk 'env A=1 pkill x' 2
chk '(pkill x)' 2; chk 'echo $(pkill x)' 2; chk 'a && pkill x' 2
chk '$K x' 0; chk 'sudo -u root pkill x' 0; chk 'p=$(pgrep x); kill $p' 0
rm -rf "$T"
echo "RESULT examples=$n count"; echo "RESULT mismatches=$bad count"
echo "RESULT thread_factor=1.000"; echo "RESULT load1=$(cut -d' ' -f1 /proc/loadavg)"; echo "RESULT swapins=0"
